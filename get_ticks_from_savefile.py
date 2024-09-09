from zipfile import ZipFile
from struct import Struct
import zlib
import io
import argparse


debug = False


# ====================================
class Deserializer:
    u16 = Struct("<H")
    u32 = Struct("<I")

    def __init__(self, stream):
        self.stream = stream
        self.version = tuple(self.read_u16() for i in range(4))

    def print_tell(self):
        if debug:
            print(hex(self.stream.tell()))

    def read(self, n):
        return self.stream.read(n)

    def read_fmt(self, fmt):
        return fmt.unpack(self.read(fmt.size))[0]

    def read_u8(self):
        return self.read(1)[0]

    def read_bool(self):
        return bool(self.read_u8())

    def read_u16(self):
        return self.read_fmt(self.u16)

    def read_u32(self):
        return self.read_fmt(self.u32)

    def read_double(self):
        return self.read_fmt(Struct("d"))

    def read_str(self, dtype=None):
        if self.version >= (0, 16, 0, 0):
            length = self.read_optim(dtype or self.u32)
        else:
            length = self.read_fmt(dtype or self.u32)

        return self.read(length).decode("utf-8")

    def read_optim(self, dtype):
        if self.version >= (0, 14, 14, 0):
            byte = self.read_u8()
            if byte != 0xFF:
                return byte
        return self.read_fmt(dtype)

    def read_optim_u16(self):
        return self.read_optim(self.u16)

    def read_optim_u32(self):
        return self.read_optim(self.u32)

    def read_optim_str(self):
        length = self.read_optim_u32()
        return self.read(length).decode("utf-8")

    def read_optim_tuple(self, dtype, num):
        return tuple(self.read_optim(dtype) for i in range(num))


# ====================================
# PropertyTree::loadInternal<MapDeserialiser>(&this->startupModSettings, input);
def get_tree_pars(ds):
    def loadImmutableString(ds):
        s = ds.read_u8()
        if s == 0:
            length = ds.read_u8()
            if length == 0xFF:
                length = ds.read_u32()
            s = ds.read(length).decode("utf-8")
        ds.print_tell()
        return s

    ds.print_tell()
    par1 = ds.read_u8()
    par2 = ds.read_u8()
    ds.print_tell()
    if par1 > 5 or par2 > 1:
        raise Exception("invalid parameters")
    if par1 == 1:
        # read bool?
        return ds.read_bool()
    elif par1 == 2:
        # read double?
        return ds.read_double()
    elif par1 == 3:
        return loadImmutableString(ds)
    elif par1 != 5:
        raise Exception("invalid parameters")
    else:
        res = {}
        count = ds.read_u32()
        ds.print_tell()
        for i in range(count):
            name = loadImmutableString(ds)
            val = get_tree_pars(ds)
            res[name] = val
        return res


# ====================================
class SaveFile:
    def __init__(self, filename):
        zf = ZipFile(filename, "r")
        datfile = None

        for f in zf.namelist():
            if f.endswith("/level.dat"):
                datfile = f
                break
            if f.endswith("/level.dat0"):
                datfile = f
                break

        if not datfile:
            raise IOError("level.dat not found in save file")

        file = io.BytesIO(zlib.decompress(zf.open(datfile, "r").read()))
        ds = Deserializer(file)
        self.version = self.version_str(ds.version)

        ds.print_tell()

        # qualityVersion
        self.qualityVersion = ds.read_u8()

        # campaignName
        self.campaign = ds.read_str()
        ds.print_tell()

        # levelName
        self.name = ds.read_str()
        ds.print_tell()

        # modName
        self.base_mod = ds.read_str()
        ds.print_tell()

        # 0: Normal, 1: Old School, 2: Hardcore
        self.difficulty = ds.read_u8()
        ds.print_tell()

        self.finished = ds.read_bool()
        ds.print_tell()

        self.player_won = ds.read_bool()
        ds.print_tell()

        self.next_level = ds.read_str()  # usually empty
        ds.print_tell()

        if ds.version >= (0, 12, 0, 0):
            self.can_continue = ds.read_bool()
            self.finished_but_continuing = ds.read_bool()

        ds.print_tell()
        self.saving_replay = ds.read_bool()
        ds.print_tell()

        if ds.version >= (0, 16, 0, 0):
            self.allow_non_admin_debug_options = ds.read_bool()
        ds.print_tell()

        self.loaded_from = self.version_str(ds.read_optim_tuple(ds.u16, 3))
        ds.print_tell()
        self.loaded_from_build = ds.read_u16()
        ds.print_tell()

        self.allowed_commands = ds.read_u8()
        ds.print_tell()
        if ds.version <= (0, 13, 0, 87):
            if not self.allowed_commands:
                self.allowed_commands = 2
            else:
                self.allowed_commands = 1
        ds.print_tell()

        self.stats = {}
        if ds.version <= (0, 13, 0, 42):
            num_stats = ds.read_u32()
            for i in range(num_stats):
                force_id = ds.read_u8()
                self.stats[force_id] = []
                for j in range(3):
                    st = {}
                    length = ds.read_u32()
                    for k in range(length):
                        k = ds.read_u16()
                        v = ds.read_u32()
                        st[k] = v
                    self.stats[force_id].append(st)

        self.mods = {}
        if ds.version >= (0, 16, 0, 0):
            num_mods = ds.read_optim_u32()
        else:
            num_mods = ds.read_u32()

        ds.print_tell()
        for i in range(num_mods):
            if debug:
                print(hex(file.tell()))
            name = ds.read_optim_str()
            version = ds.read_optim_tuple(ds.u16, 3)
            if ds.version > (0, 15, 0, 91):
                ds.read_u32()  # CRC
            self.mods[name] = self.version_str(version)
            if debug:
                print(hex(file.tell()))

        self.startupSettingsCrc = ds.read_u32()  # =0 ???
        ds.print_tell()

        self.PropertyTree = get_tree_pars(ds)

        self.updateTick = ds.read_u32()
        self.entityTick = ds.read_u32()
        self.ticksPlayed = ds.read_u32()

    @staticmethod
    def version_str(ver):
        return ".".join(str(x) for x in ver)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="get ticks from from the save.")
    parser.add_argument("save_file_name", nargs="?", default="Bob - 600.zip")
    opt = parser.parse_args()

    try:
        sf = SaveFile(opt.save_file_name)
    except Exception as e:
        print("Error!: ", opt.save_file_name, e)
        exit(2)

    print(opt.save_file_name, end=" : ")
    print("updateTick = {0:}(0x{0:X})".format(sf.updateTick), end=" ")
    print("entityTick = {0:}(0x{0:X})".format(sf.entityTick), end=" ")
    print("ticksPlayed = {0:}(0x{0:X})".format(sf.ticksPlayed))
