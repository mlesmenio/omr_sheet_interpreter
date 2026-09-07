from pdf2image import convert_from_path

SHEET_PATH = "/app/sheet_files/"

pages = convert_from_path(SHEET_PATH + "wheels_on_the_bus.pdf", dpi=300)

for i, page in enumerate(pages):
    page.save(SHEET_PATH + f"wheels_on_the_bus_{i}.png", "PNG")