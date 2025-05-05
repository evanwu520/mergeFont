import fontforge
import os
import tempfile

# Open the base and merge fonts
base = fontforge.open("baseXX.ttf")
merge = fontforge.open("mergeXX.ttf")

# Copy all glyphs from merge font, including those without Unicode
for merge_glyph in merge.glyphs():
    name = merge_glyph.glyphname
    if name not in base:
        try:
            # Create a new glyph in the base font
            new_glyph = base.createChar(-1, name)

            # Copy glyph content from merge font
            merge.selection.select(name)
            merge.copy()

            # Paste into the base font
            base.selection.select(name)
            base.paste()

            # Copy metrics, converting to integers to avoid float errors
            new_glyph.width = int(merge_glyph.width)
            new_glyph.vwidth = int(merge_glyph.vwidth) if merge_glyph.vwidth else 0
            new_glyph.left_side_bearing = int(merge_glyph.left_side_bearing)
            new_glyph.right_side_bearing = int(merge_glyph.right_side_bearing)

            # Log glyphs without Unicode (e.g., uni07DB.fina)
            if merge_glyph.unicode == -1:
                print(f"Copied glyph {name} (no Unicode)")
            else:
                print(f"Copied glyph {name} (Unicode: U+{merge_glyph.unicode:04X})")

        except Exception as e:
            print(f"Error copying glyph {name}: {e}")

# Copy OpenType features (GSUB, GPOS)
try:
    # Create a temporary .fea file for merge font's features
    with tempfile.NamedTemporaryFile(suffix=".fea", delete=False) as temp_fea:
        fea_file = temp_fea.name
        merge.generateFeatureFile(fea_file)
        print(f"Generated feature file: {fea_file}")

    # Merge the features into the base font
    base.mergeFeature(fea_file)
    print("OpenType features copied successfully")

    # Clean up the temporary file
    os.remove(fea_file)

except Exception as e:
    print(f"Error copying OpenType features: {e}")

# Validate the font before generating
validation_state = base.validate()
if validation_state != 0:
    print(f"Font validation issues: {validation_state}")

# Generate the output font
base.generate("outXXX.ttf")

# Close fonts
base.close()
merge.close()

print("Font merging completed!")