from panda3d.core import Datagram, DatagramIterator
from .BamFactory import BamFactory
from .BamGlobals import *

"""
  TOONTOWN ALPHA COMBINER
  First written for use in PANDORA

  Author: Disyer
  Date: 2020/06/13
"""
class BamFile(object):
    HEADER = b'pbj\x00\n\r'

    def __init__(self):
        self.header_size = -1
        self.bam_major_ver = -1
        self.bam_minor_ver = -1
        self.file_endian = -1
        self.stdfloat_double = -1
        self.nesting_level = -1
        self.type_handles = {}
        self.objects = []
        self.file_datas = []
        self.bam_factory = BamFactory()

    def get_handle_id_by_name(self, handle_name):
        if not isinstance(handle_name, str):
            return handle_name

        for handle_id, handle in self.type_handles.items():
            if handle['name'] == handle_name:
                return handle_id

    def find_parent(self, handle_id, parent_id):
        handle = self.type_handles[handle_id]
        parents = list(handle['parent_classes'])

        if parent_id in parents:
            return True

        for parent_class in parents:
            if self.find_parent(parent_class, parent_id):
                return True

        return False

    def find_children(self, parent_id):
        return [handle_id for handle_id in self.type_handles.keys() if self.find_parent(handle_id, parent_id)]

    def find_related(self, parent_id):
        parent_id = self.get_handle_id_by_name(parent_id)

        if parent_id is None:
            return []

        children = self.find_children(parent_id)

        if parent_id not in children:
            children.append(parent_id)

        return children

    def load(self, f):
        if f.read(len(self.HEADER)) != self.HEADER:
            raise Exception('Invalid BAM header.')

        dg = Datagram(f.read())
        di = DatagramIterator(dg)
        self.header_size = di.get_uint32()
        self.bam_major_ver = di.get_uint16()
        self.bam_minor_ver = di.get_uint16()
        self.version = (self.bam_major_ver, self.bam_minor_ver)
        self.type_handles = {}
        self.objects = []
        self.file_datas = []

        if self.version >= (5, 0):
            self.file_endian = di.get_uint8()
        else:
            self.file_endian = 1

        if self.version >= (6, 27):
            self.stdfloat_double = di.get_bool()
        else:
            self.stdfloat_double = False

        self.nesting_level = 0

        # New object stream format: read object hierarchy
        while di.getRemainingSize() > 0:
            self.read_object_code(di)

    def read_datagram(self, di):
        num_bytes = di.get_uint32()
        data = di.extractBytes(num_bytes)
        dg = Datagram(data)
        return dg

    def read_handle(self, di, parent=None):
        handle_id = di.get_uint16()

        if handle_id == 0:
            return handle_id

        if handle_id not in self.type_handles:
            # Registering a new handle!
            # Let's read the type information.
            name = di.get_string()

            num_parent_classes = di.get_uint8()
            parent_classes = []

            for i in range(num_parent_classes):
                parent_classes.append(self.read_handle(di))

            self.type_handles[handle_id] = {'name': name, 'parent_classes': parent_classes}

        return handle_id

    def read_freed_object_codes(self, di):
        obj_ids = []

        while di.get_remaining_size() > 0:
            obj_ids.append(read_pointer(di))

        return obj_ids

    def read_file_data(self, di):
        num_bytes = di.get_uint32()

        # (uint32_t) -1
        if num_bytes == 2**32 - 1:
            num_bytes = di.get_uint64()

        return di.extractBytes(num_bytes)

    def read_object_code(self, di):
        dg = self.read_datagram(di)
        dgi = DatagramIterator(dg)

        if self.version >= (6, 21):
            opcode = dgi.get_uint8()
        else:
            opcode = BOC_adjunct

        if opcode == BOC_push:
            self.nesting_level += 1
            return self.read_object(dgi)
        elif opcode == BOC_pop:
            self.nesting_level -= 1
        elif opcode == BOC_adjunct:
            return self.read_object(dgi)
        elif opcode == BOC_remove:
            self.read_freed_object_codes(dgi)
            return self.read_object_code(di)
        elif opcode == BOC_file_data:
            self.file_datas.append(self.read_file_data(dgi))
            return self.read_object_code(di)

    def read_object_from_dg(self, di):
        dg = self.read_datagram(di)
        dgi = DatagramIterator(dg)
        return self.read_object(dgi)

    def read_object(self, dgi):
        handle_id = self.read_handle(dgi)
        obj_id = read_pointer(dgi)
        data = dgi.extract_bytes(dgi.get_remaining_size())

        handle_name = self.type_handles[handle_id]['name']
        self.objects.append({'handle_id': handle_id, 'handle_name': handle_name, 'obj_id': obj_id, 'data': data})

    def write_handle(self, dg, handle_id, written_handles):
        dg.add_uint16(handle_id)

        if handle_id == 0:
            # Panda does not read any further information for handle_id == 0
            return
        if handle_id in written_handles:
            # We've already written this handle, we don't have to do it again.
            return

        # We haven't written any handles yet...
        handle = self.type_handles[handle_id]
        parent_classes = handle['parent_classes']

        written_handles.append(handle_id) # i forgot to write this line lol

        dg.add_string(handle['name'])
        dg.add_uint8(len(parent_classes))

        for handle_id in parent_classes:
            # Write all of our parent handles.
            self.write_handle(dg, handle_id, written_handles)

    def write_file_data(self, dg, data):
        num_bytes = len(data)

        if num_bytes >= (2**32 - 1):
            dg.add_uint32(2**32 - 1)
            dg.add_uint64(num_bytes)
        else:
            dg.add_uint32(num_bytes)

        dg.append_data(data)

    def write_object(self, dg, opcode, obj=None, written_handles=None):
        obj_dg = Datagram()

        if self.version >= (6, 21):
            obj_dg.add_uint8(opcode)

        if obj is not None:
            self.write_handle(obj_dg, obj['handle_id'], written_handles)
            write_pointer(obj_dg, obj['obj_id'])
            obj_dg.appendData(obj['data'])

        self.write_datagram(obj_dg, dg)

    def write_datagram(self, dg, target_dg):
        msg = dg.getMessage()

        target_dg.add_uint32(len(msg))
        target_dg.append_data(msg)

    def write(self, f, target_version):
        dg = Datagram()
        dg.appendData(self.HEADER)

        if target_version >= (6, 27):
            header_size = 6
        elif target_version >= (5, 0):
            header_size = 5
        else:
            header_size = 4

        bam_major_ver, bam_minor_ver = target_version
        dg.add_uint32(header_size)
        dg.add_uint16(bam_major_ver)
        dg.add_uint16(bam_minor_ver)

        if header_size >= 5:
            dg.add_uint8(self.file_endian)

        if header_size >= 6:
            dg.add_bool(self.stdfloat_double)

        written_handles = []

        if self.objects:
            self.write_object(dg, BOC_push, self.objects[0], written_handles)

            for obj in self.objects[1:]:
                self.write_object(dg, BOC_adjunct, obj, written_handles)

        for data in self.file_datas:
            self.write_file_data(dg, data)

        if self.version >= (6, 21):
            self.write_object(dg, BOC_pop)

        f.write(dg.getMessage())

    def __str__(self):
        return 'Panda3D BAM file version {0}.{1} ({2}, {3})'.format(
            self.bam_major_ver, self.bam_minor_ver,
            'Big-endian' if self.file_endian == 0 else 'Little-endian',
            '64-bit' if self.stdfloat_double else '32-bit'
        )