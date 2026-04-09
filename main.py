# -*- coding: utf-8 -*-
#
# 	Colour Palette from CSV Generator
#
# 	Copyright (C) 2026 by Carl Birch
#
# 	This program is free software: you can redistribute it and/or modify
# 	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
# 	(at your option) any later version.
#
# 	This program is distributed in the hope that it will be useful,
# 	but WITHOUT ANY WARRANTY; without even the implied warranty of
# 	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# 	GNU General Public License for more details.
#
# 	You should have received a copy of the GNU General Public License
# 	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import csv
import os
import shutil
import zipfile
import hashlib
from datetime import datetime

def cmyk_to_hex(cp, mp, yp, kp):
    c = int(cp * 2.55)
    m = int(mp * 2.55)
    y = int(yp * 2.55)
    k = int(kp * 2.55)
    return "#{:02x}{:02x}{:02x}{:02x}".format(c,m,y,k)

def main(file_format, input, output):

    output_file_format = ""
    
    match file_format:
        case "gpl":
            output_file_format = f"{output}.gpl"
        case "scribus":
            output_file_format = f"{output}.xml"
        case "krita":
            output_file_format = f"{output}.gpl"
    
    with open(input, newline='') as csvfile, open(output_file_format, "w") as out:
       code_reader = csv.reader(csvfile, delimiter=',')
       next(code_reader)

       match file_format:
           case "gpl":
               out.write(f"GIMP Palette\n")
               out.write(f"Name: {output}\n")
               out.write(f"Columns: 0\n")
               for row in code_reader:
                   hex = row[5].lstrip('#')
                   r = int(hex[0:2], 16)
                   g = int(hex[2:4], 16)
                   b = int(hex[4:6], 16)
                   out.write(f"{r} {g} {b} {row[0]}\n")

           case "scribus":
               out.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
               out.write(f'<SCRIBUSCOLORS Name="{output}">\n')
               for row in code_reader:
                   hex = cmyk_to_hex(float(row[1]), float(row[2]), float(row[3]), float(row[4]))
                   out.write(f'<COLOR Spot="0" Register="0" Name="{row[0]}" CMYK="{hex}"/>\n')
               out.write(f"</SCRIBUSCOLORS>")

           case "krita":
               os.mkdir("palettes")
               out.write(f"GIMP Palette\n")
               out.write(f"Name: {output}\n")
               out.write(f"Columns: 0\n")
               for row in code_reader:
                   hex = row[5].lstrip('#')
                   r = int(hex[0:2], 16)
                   g = int(hex[2:4], 16)
                   b = int(hex[4:6], 16)
                   out.write(f"{r} {g} {b} {row[0]}\n")
            
    if file_format == "krita":

        hasher = hashlib.md5()

        with open(output_file_format, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        palette_hash = hasher.hexdigest()
        
        with open("mimetype", "w") as mt:
            mt.write(f"application/x-krita-resourcebundle")

        with open("meta.xml", "w") as meta:
            meta.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
            meta.write(f'<meta:meta xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:dc="http://purl.org/dc/elements/1.1">\n')
            meta.write(f'<meta:generator>Krita (6.0.1)</meta:generator>\n')
            meta.write(f"<meta:bundle-version>1</meta:bundle-version>\n")
            meta.write(f"<dc:author>CSV to Palette Generator</dc:author>\n")
            meta.write(f'<dc:title>{output}</dc:title>\n')
            meta.write(f"<dc:description>{output} Bundle Generated with CSV to Palette Generator</dc:description>\n")
            meta.write(f'<meta:inital-creator>{output} Generated with CSV to Palette Generator</meta:inital-creator>\n')
            meta.write(f'<dc:creator>{output} Generated with CSV to Palette Generator</dc:creator>\n')
            meta.write(f'<meta:creation-date>{datetime.now().strftime("%d/%m/%Y")}</meta:creation-date>\n')
            meta.write(f'<meta:dc-date>{datetime.now().strftime("%d/%m/%Y")}</meta:dc-date>\n')
            meta.write(f'<meta:email></meta:email>\n')
            meta.write(f'<meta:license>CC-BY-SA</meta:license>\n')
            meta.write(f'<meta:website></meta:website>\n')
            meta.write(f'<meta:meta-userdefined meta:name="email" meta:value=""/>\n')
            meta.write(f'<meta:meta-userdefined meta:name="license" meta:value="CC-BY-SA"/>\n')
            meta.write(f'<meta:meta-userdefined meta:name="website" meta:value="http://"/>\n')
            meta.write(f'</meta:meta>')
            
        os.mkdir("META-INF")

        with open("manifest.xml", "w") as mani:
            mani.write(f'<?xml version="1.0" encoding="UTF-8"?>\n')
            mani.write(f'<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0" manifest:version="1.2">\n')
            mani.write(f'<manifest:file-entry manifest:media-type="application/x-krita-resourcebundle" manifest:full-path="/"/>\n')
            mani.write(f'<manifest:file-entry manifest:media-type="palettes" manifest:full-path="palettes/{output_file_format}" manifest:md5sum="{palette_hash}"/>\n')
            mani.write(f'</manifest:manifest>')

        shutil.move("manifest.xml", "META-INF")
        shutil.move(output_file_format, "palettes")
        zipname = f"{output}.bundle"
        with zipfile.ZipFile(zipname, "w") as zippy:
            zippy.write("meta.xml")
            zippy.write("mimetype")
            zippy.write("palettes")
            zippy.write("palettes/" + output_file_format)
            zippy.write("META-INF")
            zippy.write("META-INF/manifest.xml")
        os.remove("mimetype")
        os.remove("meta.xml")
        os.remove("palettes/" + output_file_format)
        os.removedirs("palettes")
        os.remove("META-INF/manifest.xml")
        os.removedirs("META-INF")

if __name__ == "__main__":

    if len(sys.argv) != 4:
        print('Usage: python main.py "format" "input" "output"')
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
