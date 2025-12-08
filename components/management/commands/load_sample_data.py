from django.core.management.base import BaseCommand
from components.models import Component, ComponentSupplier, PurchaseOrder, PurchaseOrderItem
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Load sample component data into the database'

    def handle(self, *args, **options):
        # Clear existing data
        Component.objects.all().delete()
        
        # Component types and their typical values
        resistors = [
            ('10Ω', 'Vishay', 'Digikey', 'RNCP0805FTD10R0CT-ND'),
            ('22Ω', 'Yageo', 'Mouser', '603-RC0805FR-0722RL'),
            ('47Ω', 'Bourns', 'Farnell', '2059151'),
            ('100Ω', 'KOA Speer', 'Digikey', '2019-RK73H2ATTD1000FCT-ND'),
            ('220Ω', 'Vishay', 'Mouser', '71-CRCW0805220RFKEA'),
            ('470Ω', 'Yageo', 'Farnell', '9331662'),
            ('1kΩ', 'Bourns', 'Digikey', '118-CR0805-FX-1001ELFCT-ND'),
            ('2.2kΩ', 'KOA Speer', 'Mouser', '660-RK73H2ATTD2201F'),
            ('4.7kΩ', 'Vishay', 'Farnell', '2138731'),
            ('10kΩ', 'Yageo', 'Digikey', 'YAG3561CT-ND'),
            ('22kΩ', 'Bourns', 'Mouser', 'CR0805-JW-223ELF'),
            ('47kΩ', 'KOA Speer', 'Farnell', '2447521'),
            ('100kΩ', 'Vishay', 'Digikey', 'CRCW0805100KFKEA'),
            ('220kΩ', 'Yageo', 'Mouser', '603-RC0805FR-07220KL'),
            ('470kΩ', 'Bourns', 'Farnell', '2447665'),
        ]
        
        capacitors = [
            ('1pF', 'Murata', 'Digikey', '490-1666-1-ND'),
            ('10pF', 'AVX', 'Mouser', '581-08055A100JAT2A'),
            ('22pF', 'KEMET', 'Farnell', '1414619'),
            ('47pF', 'Samsung', 'Digikey', '1276-1003-1-ND'),
            ('100pF', 'TDK', 'Mouser', '810-C2012X7R2A101K'),
            ('220pF', 'Murata', 'Farnell', '2320856'),
            ('470pF', 'AVX', 'Digikey', '478-1395-1-ND'),
            ('1nF', 'KEMET', 'Mouser', '80-C0805C102K5R'),
            ('10nF', 'Samsung', 'Farnell', '2534471'),
            ('22nF', 'TDK', 'Digikey', '445-1418-1-ND'),
            ('47nF', 'Murata', 'Mouser', '81-GRM21BR71H473KA1L'),
            ('100nF', 'AVX', 'Farnell', '197427'),
            ('220nF', 'KEMET', 'Digikey', '399-1147-1-ND'),
            ('470nF', 'Samsung', 'Mouser', '187-CL21B474KBFNNNE'),
            ('1μF', 'TDK', 'Farnell', '2346885'),
            ('2.2μF', 'Murata', 'Digikey', '490-3261-1-ND'),
            ('4.7μF', 'AVX', 'Mouser', '581-08055C475KAT2A'),
            ('10μF', 'KEMET', 'Farnell', '2320856'),
            ('22μF', 'Samsung', 'Digikey', '1276-6455-1-ND'),
            ('47μF', 'TDK', 'Mouser', '810-C3216X7R1A476K'),
            ('100μF', 'Panasonic', 'Farnell', '1907168'),
            ('220μF', 'Nichicon', 'Digikey', '493-2203-ND'),
        ]
        
        ics = [
            ('74HC00', 'Texas Instruments', 'Mouser', '595-SN74HC00N'),
            ('74HC04', 'NXP', 'Digikey', '568-11697-5-ND'),
            ('74HC08', 'ON Semi', 'Farnell', '3121405'),
            ('74HC32', 'Texas Instruments', 'Mouser', '595-SN74HC32N'),
            ('74HC74', 'NXP', 'Digikey', '568-3046-5-ND'),
            ('LM358', 'Texas Instruments', 'Farnell', '3118467'),
            ('LM741', 'STMicroelectronics', 'Mouser', '511-LM741CN'),
            ('NE555', 'Texas Instruments', 'Digikey', '296-1411-5-ND'),
            ('ATmega328P', 'Microchip', 'Mouser', '556-ATMEGA328P-PU'),
            ('STM32F103', 'STMicroelectronics', 'Farnell', '1447930'),
            ('ESP32', 'Espressif', 'Digikey', '1965-1000-ND'),
            ('Arduino Nano', 'Arduino', 'Mouser', '782-A000005'),
            ('Raspberry Pi Pico', 'Raspberry Pi', 'Farnell', '3377413'),
            ('LM7805', 'Texas Instruments', 'Digikey', '296-1840-5-ND'),
            ('LM317', 'STMicroelectronics', 'Mouser', '511-LM317T'),
        ]
        
        diodes_transistors = [
            ('1N4148', 'Vishay', 'Mouser', '78-1N4148'),
            ('1N4001', 'ON Semi', 'Digikey', '1N4001FSCT-ND'),
            ('1N5819', 'Diodes Inc', 'Farnell', '1861611'),
            ('LED Red 5mm', 'Kingbright', 'Mouser', '604-WP7113ID'),
            ('LED Green 5mm', 'Lite-On', 'Digikey', '160-1144-ND'),
            ('LED Blue 5mm', 'Kingbright', 'Farnell', '2373511'),
            ('LED Yellow 5mm', 'Lite-On', 'Mouser', '859-LTL-4221N'),
            ('LED White 5mm', 'Cree', 'Digikey', 'C503B-WAN-CBABA151-ND'),
            ('2N2222', 'Fairchild', 'Farnell', '1593969'),
            ('BC547', 'ON Semi', 'Mouser', '512-BC547BTA'),
            ('2N3904', 'Central Semi', 'Digikey', '2N3904CS-ND'),
            ('BC337', 'NXP', 'Farnell', '1574426'),
            ('MOSFET 2N7000', 'Fairchild', 'Mouser', '512-2N7000'),
            ('IRF520', 'Infineon', 'Digikey', 'IRF520PBF-ND'),
        ]
        
        other_components = [
            ('Push Button 6x6mm', 'Omron', 'Farnell', '1960997'),
            ('Rotary Encoder', 'Bourns', 'Mouser', '652-PEC11R-4215F-S24'),
            ('Potentiometer 10kΩ', 'Alpha', 'Digikey', 'RV09AF-40-20K-A10K-ND'),
            ('Buzzer 5V', 'CUI Devices', 'Farnell', '1453200'),
            ('Crystal 16MHz', 'Abracon', 'Mouser', '815-ABL-16-B2'),
            ('Crystal 32.768kHz', 'Epson', 'Digikey', 'SER3686CT-ND'),
            ('Fuse 1A', 'Littelfuse', 'Farnell', '1679452'),
            ('Relay 5V', 'Omron', 'Mouser', '653-G5LE-1-VD-5VDC'),
            ('Optocoupler 4N35', 'Vishay', 'Digikey', '4N35-ND'),
            ('7-Segment Display', 'Kingbright', 'Farnell', '1142641'),
            ('LCD 16x2', 'Displaytech', 'Mouser', '763-162A-BC-3LP'),
            ('Temperature Sensor LM35', 'Texas Instruments', 'Digikey', '296-1419-5-ND'),
            ('Accelerometer ADXL345', 'Analog Devices', 'Farnell', '1848308'),
            ('Ultrasonic Sensor HC-SR04', 'Generic', 'Mouser', '485-3880'),
        ]

        created_count = 0
        locations = ['Drawer A1', 'Drawer A2', 'Drawer B1', 'Drawer B2', 'Shelf C1', 'Shelf C2', 'Shelf C3', 'Box D1', 'Box D2', 'Cabinet E1']
        suppliers = ['Digikey', 'Mouser', 'Farnell', 'RS Components', 'Newark', 'Arrow']
        
        # Create resistors
        for value, manufacturer, supplier, part_num in resistors:
            stock = random.randint(0, 500)
            min_level = random.randint(10, 50)
            Component.objects.create(
                description='Resistor',
                value=value,
                manufacturer=manufacturer,
                supplier_name=supplier,
                supplier_part_number=part_num,
                quantity_in_stock=stock,
                minimum_stock_level=min_level,
                location=random.choice(locations),
                notes=f'{random.choice(["1/8W", "1/4W", "1/2W"])} {random.choice(["1%", "5%"])} tolerance'
            )
            created_count += 1

        # Create capacitors
        for value, manufacturer, supplier, part_num in capacitors:
            stock = random.randint(0, 300)
            min_level = random.randint(5, 30)
            cap_type = random.choice(['Ceramic', 'Electrolytic', 'Tantalum', 'Film'])
            voltage = random.choice(['16V', '25V', '35V', '50V', '100V'])
            Component.objects.create(
                description='Capacitor',
                value=value,
                manufacturer=manufacturer,
                supplier_name=supplier,
                supplier_part_number=part_num,
                quantity_in_stock=stock,
                minimum_stock_level=min_level,
                location=random.choice(locations),
                notes=f'{cap_type} {voltage}'
            )
            created_count += 1

        # Create ICs
        for value, manufacturer, supplier, part_num in ics:
            stock = random.randint(0, 50)
            min_level = random.randint(2, 10)
            Component.objects.create(
                description='IC',
                value=value,
                manufacturer=manufacturer,
                supplier_name=supplier,
                supplier_part_number=part_num,
                quantity_in_stock=stock,
                minimum_stock_level=min_level,
                location=random.choice(locations),
                notes=random.choice(['DIP-8', 'DIP-14', 'DIP-16', 'SOIC-8', 'QFP-32', 'BGA'])
            )
            created_count += 1

        # Create diodes and transistors
        for value, manufacturer, supplier, part_num in diodes_transistors:
            stock = random.randint(0, 200)
            min_level = random.randint(5, 25)
            if 'LED' in value:
                description = 'LED'
                notes = f'{random.choice(["3.2V", "2.1V", "1.8V"])} forward voltage, 20mA max current'
            elif any(x in value for x in ['1N', 'Diode']):
                description = 'Diode'
                notes = f'{random.choice(["75V", "50V", "30V"])} reverse voltage'
            else:
                description = 'Transistor'
                notes = random.choice(['NPN', 'PNP', 'N-Channel MOSFET', 'P-Channel MOSFET'])
            
            Component.objects.create(
                description=description,
                value=value,
                manufacturer=manufacturer,
                supplier_name=supplier,
                supplier_part_number=part_num,
                quantity_in_stock=stock,
                minimum_stock_level=min_level,
                location=random.choice(locations),
                notes=notes
            )
            created_count += 1

        # Create other components
        for value, manufacturer, supplier, part_num in other_components:
            stock = random.randint(0, 100)
            min_level = random.randint(2, 15)
            if 'Button' in value:
                description = 'Push Button'
                notes = 'Tactile switch, 4-pin through-hole'
            elif 'Display' in value or 'LCD' in value:
                description = 'Display'
                notes = 'Character display with backlight'
            elif 'Sensor' in value:
                description = 'Sensor'
                notes = 'Analog/Digital sensor module'
            elif 'Crystal' in value:
                description = 'Crystal'
                notes = 'Quartz crystal oscillator'
            else:
                description = value.split()[0]
                notes = 'Electronic component'
            
            Component.objects.create(
                description=description,
                value=value,
                manufacturer=manufacturer,
                supplier_name=supplier,
                supplier_part_number=part_num,
                quantity_in_stock=stock,
                minimum_stock_level=min_level,
                location=random.choice(locations),
                notes=notes
            )
            created_count += 1

        # Add some additional random components to reach 100
        component_types = ['Inductor', 'Transformer', 'Switch', 'Connector', 'Heat Sink', 'PCB']
        manufacturers_pool = ['Texas Instruments', 'Analog Devices', 'Microchip', 'STMicroelectronics', 'NXP', 'Infineon']
        
        while created_count < 100:
            comp_type = random.choice(component_types)
            value_suffix = random.choice(['', 'A', 'B', 'C', '001', '002'])
            Component.objects.create(
                description=comp_type,
                value=f'{comp_type}-{random.randint(100, 999)}{value_suffix}',
                manufacturer=random.choice(manufacturers_pool),
                supplier_name=random.choice(suppliers),
                supplier_part_number=f'{random.choice(["ABC", "DEF", "GHI"])}-{random.randint(1000, 9999)}',
                quantity_in_stock=random.randint(0, 100),
                minimum_stock_level=random.randint(5, 20),
                location=random.choice(locations),
                notes=f'Generic {comp_type.lower()} component'
            )
            created_count += 1

        # Create sample suppliers first
        suppliers_created = 0
        supplier_data = [
            ('Digikey', 'John Smith', '555-0101', 'orders@digikey.com', 'https://www.digikey.com', '123 Main St, Minneapolis, MN', 'ACME Electronics', 'ACC001'),
            ('Mouser', 'Jane Doe', '555-0102', 'sales@mouser.com', 'https://www.mouser.com', '456 Oak Ave, Mansfield, TX', 'ACME Electronics', 'ACC002'),
            ('Farnell', 'Bob Wilson', '555-0103', 'support@farnell.com', 'https://www.farnell.com', '789 Pine St, London, UK', 'ACME Electronics', 'ACC003'),
            ('Arrow', 'Alice Johnson', '555-0104', 'info@arrow.com', 'https://www.arrow.com', '321 Elm Dr, Denver, CO', 'ACME Electronics', 'ACC004'),
        ]
        
        for name, contact, phone, email, website, address, account_name, account_num in supplier_data:
            supplier, created = ComponentSupplier.objects.get_or_create(
                supplier=name,
                defaults={
                    'contact_email': email,
                    'phone_number': phone,
                    'website': website,
                    'address': address,
                    'account_name': account_name,
                    'account_number': account_num,
                    'notes': f'Sample supplier data for {name}'
                }
            )
            if created:
                suppliers_created += 1
        
        # Create sample purchase orders
        suppliers = ComponentSupplier.objects.all()
        components = list(Component.objects.all()[:20])  # Use first 20 components
        
        po_count = 0
        statuses = ['draft', 'pending', 'ordered', 'received']
        
        for i in range(5):  # Create 5 sample purchase orders
            supplier = random.choice(suppliers)
            status = random.choice(statuses)
            days_ago = random.randint(1, 30)
            order_date = date.today() - timedelta(days=days_ago)
            
            # Create expected date 1-4 weeks from creation
            expected_delivery = order_date + timedelta(days=random.randint(7, 28))
            
            po = PurchaseOrder.objects.create(
                supplier=supplier,
                status=status,
                expected_delivery=expected_delivery,
                notes=f'Sample purchase order {i+1} for testing purposes'
            )
            po.order_date = order_date  # Set custom creation date
            po.save()
            
            # Add 2-5 random components to each PO
            num_items = random.randint(2, 5)
            selected_components = random.sample(components, num_items)
            
            for component in selected_components:
                quantity = random.randint(1, 20)
                unit_cost = round(random.uniform(0.10, 50.00), 2)
                
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    component=component,
                    quantity=quantity,
                    unit_cost=unit_cost
                )
            
            po_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {created_count} sample components, '
                f'{suppliers_created} suppliers, and {po_count} purchase orders!'
            )
        )