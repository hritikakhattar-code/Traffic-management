import os
import pandas as pd
from datetime import datetime
import cv2
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ChallanGenerator:
    """
    Class to generate challans (tickets) for speeding violations
    """
    def __init__(self, csv_file, output_dir='reports'):
        """
        Initialize the challan generator
        
        Args:
            csv_file (str): Path to CSV file with speed data
            output_dir (str): Directory to save generated challans
        """
        self.csv_file = csv_file
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def load_violations(self, min_speed=None):
        """
        Load violations from CSV file
        
        Args:
            min_speed (float, optional): Filter violations by minimum speed
            
        Returns:
            pandas.DataFrame: Filtered violations
        """
        try:
            df = pd.read_csv(self.csv_file)
            
            if min_speed is not None:
                df = df[df['speed'] >= min_speed]
                
            return df
        except Exception as e:
            print(f"Error loading violations: {e}")
            return pd.DataFrame()
    
    def generate_challan(self, vehicle_id, timestamp, speed, snapshot_path, fine_amount=100):
        """
        Generate a challan PDF for a specific violation
        
        Args:
            vehicle_id (int): Vehicle ID
            timestamp (str): Timestamp of violation
            speed (float): Detected speed
            snapshot_path (str): Path to vehicle snapshot
            fine_amount (float): Fine amount
            
        Returns:
            str: Path to generated PDF
        """
        try:
            # Create output filename
            timestamp_obj = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            formatted_time = timestamp_obj.strftime("%Y-%m-%d %H:%M:%S")
            output_file = os.path.join(self.output_dir, f"challan_vehicle_{vehicle_id}_{timestamp}.pdf")
            
            # Create PDF
            doc = SimpleDocTemplate(output_file, pagesize=letter)
            elements = []
            
            # Add styles
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            normal_style = styles['Normal']
            
            # Add title
            elements.append(Paragraph("TRAFFIC VIOLATION CHALLAN", title_style))
            elements.append(Spacer(1, 20))
            
            # Add details
            elements.append(Paragraph(f"Vehicle ID: {vehicle_id}", normal_style))
            elements.append(Paragraph(f"Date & Time: {formatted_time}", normal_style))
            elements.append(Paragraph(f"Detected Speed: {speed} km/h", normal_style))
            elements.append(Paragraph(f"Fine Amount: ${fine_amount}", normal_style))
            elements.append(Spacer(1, 20))
            
            # Add image if available
            if os.path.exists(snapshot_path):
                # Resize image for PDF
                img = cv2.imread(snapshot_path)
                if img is not None:
                    height, width = img.shape[:2]
                    max_width = 400
                    if width > max_width:
                        ratio = max_width / width
                        img = cv2.resize(img, (max_width, int(height * ratio)))
                    
                    # Save resized image
                    temp_img_path = os.path.join(self.output_dir, f"temp_{vehicle_id}.jpg")
                    cv2.imwrite(temp_img_path, img)
                    
                    # Add to PDF
                    elements.append(Paragraph("Vehicle Image:", normal_style))
                    elements.append(Image(temp_img_path, width=350, height=200))
                    
                    # Clean up temp file
                    os.remove(temp_img_path)
            
            # Build PDF
            doc.build(elements)
            return output_file
            
        except Exception as e:
            print(f"Error generating challan: {e}")
            return None
    
    def generate_all_challans(self, speed_limit=50, fine_base=100, fine_per_unit=10):
        """
        Generate challans for all violations above speed limit
        
        Args:
            speed_limit (float): Speed limit
            fine_base (float): Base fine amount
            fine_per_unit (float): Additional fine per unit over limit
            
        Returns:
            list: Paths to generated PDFs
        """
        df = self.load_violations(min_speed=speed_limit)
        generated_files = []
        
        for _, row in df.iterrows():
            # Calculate fine based on how much over the limit
            over_limit = row['speed'] - speed_limit
            fine = fine_base + (over_limit * fine_per_unit)
            
            # Generate challan
            pdf_path = self.generate_challan(
                vehicle_id=row['vehicle_id'],
                timestamp=row['timestamp'],
                speed=row['speed'],
                snapshot_path=row['snapshot_path'],
                fine_amount=fine
            )
            
            if pdf_path:
                generated_files.append(pdf_path)
                
        return generated_files
    
    def generate_summary_report(self, output_file='summary_report.pdf'):
        """
        Generate a summary report of all violations
        
        Args:
            output_file (str): Output file path
            
        Returns:
            str: Path to generated PDF
        """
        df = self.load_violations()
        if df.empty:
            return None
            
        # Calculate statistics
        total_violations = len(df)
        avg_speed = df['speed'].mean()
        max_speed = df['speed'].max()
        
        # Prepare output path
        output_path = os.path.join(self.output_dir, output_file)
        
        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        
        # Add styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        heading2_style = styles['Heading2']
        normal_style = styles['Normal']
        
        # Add title
        elements.append(Paragraph("Traffic Violations Summary Report", title_style))
        elements.append(Spacer(1, 20))
        
        # Add statistics
        elements.append(Paragraph("Summary Statistics:", heading2_style))
        elements.append(Paragraph(f"Total Violations: {total_violations}", normal_style))
        elements.append(Paragraph(f"Average Speed: {avg_speed:.1f} km/h", normal_style))
        elements.append(Paragraph(f"Maximum Speed: {max_speed:.1f} km/h", normal_style))
        elements.append(Spacer(1, 20))
        
        # Add table of violations
        elements.append(Paragraph("List of Violations:", heading2_style))
        
        # Prepare table data
        table_data = [["Vehicle ID", "Timestamp", "Speed (km/h)"]]
        for _, row in df.iterrows():
            table_data.append([str(row['vehicle_id']), row['timestamp'], f"{row['speed']:.1f}"])
            
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.