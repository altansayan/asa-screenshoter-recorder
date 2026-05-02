from PIL import Image, ImageDraw

def create_camera_icon():
    # 256x256 image with transparent background
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Camera body (Rounded rectangle)
    body_color = (45, 52, 54, 255)
    draw.rounded_rectangle([20, 80, 236, 210], radius=20, fill=body_color)
    
    # Camera flash/top part
    top_color = (99, 110, 114, 255)
    draw.rounded_rectangle([70, 40, 186, 80], radius=10, fill=top_color)
    
    # Lens outer
    lens_outer = (223, 230, 233, 255)
    draw.ellipse([88, 105, 168, 185], fill=lens_outer)
    
    # Lens inner
    lens_inner = (45, 52, 54, 255)
    draw.ellipse([103, 120, 153, 170], fill=lens_inner)
    
    # Lens reflection
    reflection = (255, 255, 255, 180)
    draw.ellipse([115, 130, 125, 140], fill=reflection)
    
    # Flash bulb
    flash_bulb = (255, 234, 167, 255)
    draw.ellipse([190, 100, 210, 120], fill=flash_bulb)
    
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

if __name__ == "__main__":
    create_camera_icon()
