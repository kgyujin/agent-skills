#!/usr/bin/env python3
"""작성자: Git 이력 참조. 작성목적: PPTX 테마 및 텍스트의 한국어 서체 지정.
작성일: 2026-10-22. Python 표준 라이브러리만 사용하며 원자적으로 ZIP을 교체한다.
"""
import os
import sys
import tempfile
import zipfile
from xml.dom import minidom

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'

def patch(filename, font):
    with zipfile.ZipFile(filename) as archive:
        entries = [(info, archive.read(info.filename)) for info in archive.infolist()]
    # Keep note-master themes separate from slide-master themes for Office compatibility.
    import posixpath
    rel_ns = 'http://schemas.openxmlformats.org/package/2006/relationships'
    contents = dict((info.filename, content) for info, content in entries)
    additions = []
    for index, (info, content) in enumerate(entries):
        if not (info.filename.startswith('ppt/notesMasters/_rels/') and info.filename.endswith('.rels')):
            continue
        document = minidom.parseString(content)
        for relationship in document.getElementsByTagNameNS(rel_ns, 'Relationship'):
            if not relationship.getAttribute('Type').endswith('/theme'):
                continue
            target = relationship.getAttribute('Target')
            original = posixpath.normpath(posixpath.join('ppt/notesMasters', target))
            if original not in contents:
                continue
            basename = 'clean-notes-' + posixpath.basename(info.filename) + '-theme.xml'
            destination = 'ppt/theme/' + basename
            if original == destination:
                continue
            relationship.setAttribute('Target', '../theme/' + basename)
            additions.append((zipfile.ZipInfo(destination), contents[original]))
            types = minidom.parseString(contents['[Content_Types].xml'])
            override = types.createElementNS(types.documentElement.namespaceURI, 'Override')
            override.setAttribute('PartName', '/' + destination)
            override.setAttribute('ContentType', 'application/vnd.openxmlformats-officedocument.theme+xml')
            types.documentElement.appendChild(override)
            contents['[Content_Types].xml'] = types.toxml(encoding='utf-8')
        entries[index] = (info, document.toxml(encoding='utf-8'))
    entries = [(info, contents['[Content_Types].xml'] if info.filename == '[Content_Types].xml' else content) for info, content in entries] + additions
    fd, temporary = tempfile.mkstemp(suffix='.pptx', dir=os.path.dirname(os.path.abspath(filename)))
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for info, content in entries:
                if info.filename.startswith('ppt/') and info.filename.endswith('.xml'):
                    document = minidom.parseString(content)
                    changed = False
                    # DOM preserves existing namespace prefixes, including mc:Ignorable values.
                    # Append font children in DrawingML schema order without moving other nodes.
                    for node in list(document.getElementsByTagNameNS(A, '*')):
                        if node.localName not in ('majorFont', 'minorFont', 'rPr', 'defRPr', 'endParaRPr'):
                            continue
                        is_theme = node.localName in ('majorFont', 'minorFont')
                        if not is_theme:
                            node.setAttribute('lang', 'ko-KR')
                        for kind in (('latin', 'ea', 'cs') if is_theme else ('ea',)):
                            children = [child for child in node.childNodes if child.nodeType == child.ELEMENT_NODE]
                            child = next((child for child in children if child.namespaceURI == A and child.localName == kind), None)
                            if child is None:
                                prefix = node.prefix or 'a'
                                child = document.createElementNS(A, prefix + ':' + kind)
                                if not node.prefix:
                                    child.setAttribute('xmlns:' + prefix, A)
                                order = {'latin': 0, 'ea': 1, 'cs': 2, 'sym': 3, 'font': 4,
                                         'hlinkClick': 5, 'hlinkMouseOver': 6, 'rtl': 7, 'extLst': 8}
                                successor = next((candidate for candidate in children
                                                  if candidate.namespaceURI == A
                                                  and order.get(candidate.localName, -1) > order[kind]), None)
                                node.insertBefore(child, successor)
                            child.setAttribute('typeface', font)
                        if is_theme:
                            for child in node.childNodes:
                                if child.nodeType == child.ELEMENT_NODE and child.namespaceURI == A and child.localName == 'font' and child.getAttribute('script') in ('Hang', 'Hans', 'Hant', 'Jpan'):
                                    child.setAttribute('typeface', font)
                        changed = True
                    if changed:
                        content = document.toxml(encoding='utf-8')
                    document.unlink()
                archive.writestr(info, content)
        os.replace(temporary, filename)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def image_size(filename):
    import struct
    import json
    with open(filename, 'rb') as source:
        header = source.read(24)
        if header.startswith(b'\x89PNG\r\n\x1a\n'):
            dimensions = struct.unpack('>II', header[16:24])
        elif header.startswith(b'\xff\xd8'):
            source.seek(2)
            dimensions = None
            while True:
                marker = source.read(1)
                if not marker:
                    break
                if marker != b'\xff':
                    continue
                marker = source.read(1)
                while marker == b'\xff':
                    marker = source.read(1)
                if marker in (b'\xd8', b'\xd9'):
                    continue
                length = struct.unpack('>H', source.read(2))[0]
                if marker and marker[0] in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                    _, height, width = struct.unpack('>BHH', source.read(5))
                    dimensions = (width, height)
                    break
                source.seek(length-2, 1)
            if dimensions is None:
                raise ValueError('JPEG dimensions missing')
        else:
            raise ValueError('Only PNG and JPEG images supported')
    print(json.dumps(dimensions))

if __name__ == '__main__':
    if sys.argv[1] == '--image-size':
        image_size(sys.argv[2])
    else:
        patch(sys.argv[1], sys.argv[2])
