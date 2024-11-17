import os
import sys
from datetime import datetime, timedelta
from PIL import Image
import piexif


def add_months(original_date, months):
    """Helper function to add months while handling year transitions."""
    new_month = original_date.month + months
    new_year = original_date.year + (new_month - 1) // 12
    new_month = (new_month - 1) % 12 + 1
    try:
        return original_date.replace(year=new_year, month=new_month)
    except ValueError:
        # Handle day overflow
        return original_date.replace(year=new_year, month=new_month, day=1)


def change_date_taken(folder_path, years=0, months=0, days=0, hours=0, minutes=0):
    increment = timedelta(days=days, hours=hours, minutes=minutes)
    # Walk through all subdirs
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                # Process common image formats
                if not file.lower().endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp", ".arw", ".cr2", ".raw")):
                    print(f"Skipping unsupported file: {file_path}")
                    continue

                # Open image and parse EXIF data
                img = Image.open(file_path)
                if not img.info.get("exif"):
                    print(f"No EXIF metadata found for: {file_path}")
                    continue
                
                exif_data = piexif.load(img.info["exif"])

                original_date = exif_data["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
                
                if original_date:
                    original_date_str = original_date.decode("utf-8")
                    original_date_dt = datetime.strptime(original_date_str, "%Y:%m:%d %H:%M:%S")
                    
                    # Apply increments
                    new_date_dt = original_date_dt + increment
                    if months or years:
                        new_date_dt = add_months(new_date_dt, months + years * 12)
                    
                    new_date_str = new_date_dt.strftime("%Y:%m:%d %H:%M:%S")
                    
                    # Update EXIF data
                    exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal] = new_date_str.encode("utf-8")
                    exif_data["Exif"][piexif.ExifIFD.DateTimeDigitized] = new_date_str.encode("utf-8")
                    
                    # Save img
                    exif_bytes = piexif.dump(exif_data)
                    img.save(file_path, format=img.format, exif=exif_bytes)
                    print(f"Updated 'Date Taken' for: {file_path}")
                else:
                    print(f"No 'Date Taken' metadata found for: {file_path}")
            
            except Exception as e:
                print(f"Failed to update 'Date Taken' for: {file_path}. Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Change 'Date Taken' for images in a folder.")
    parser.add_argument("folder_path", type=str, help="Path to the folder containing images")
    parser.add_argument("--years", type=int, default=0, help="Number of years to add")
    parser.add_argument("--months", type=int, default=0, help="Number of months to add")
    parser.add_argument("--days", type=int, default=0, help="Number of days to add")
    parser.add_argument("--hours", type=int, default=0, help="Number of hours to add")
    parser.add_argument("--minutes", type=int, default=0, help="Number of minutes to add")

    args = parser.parse_args()

    # Call
    change_date_taken(
        args.folder_path,
        years=args.years,
        months=args.months,
        days=args.days,
        hours=args.hours,
        minutes=args.minutes,
    )
