from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string


class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=150)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admins'
        verbose_name = 'Admin User'
        verbose_name_plural = 'Admin Users'

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def __str__(self) -> str:
        return self.full_name


class ClientAccount(models.Model):
    SCHOOL_PROGRAM_CHOICES = [
        ('engineering', 'School of Engineering – Civil Engineering / Other Engineering'),
        ('education', 'School of Teacher Education'),
        ('technology', 'School of Technology & Computer Studies'),
        ('management', 'School of Management & Entrepreneurship'),
        ('nursing', 'School of Nursing & Health Sciences'),
        ('criminal_justice', 'School of Criminal Justice Education'),
        ('arts_sciences', 'School of Arts & Sciences'),
    ]

    STUDENT_TYPE_CHOICES = [
        ('regular', 'Regular student'),
        ('irregular', 'Irregular student'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    student_id = models.CharField(max_length=50, blank=True)
    contact_number = models.CharField(max_length=30)
    school_program = models.CharField(
        max_length=60, choices=SCHOOL_PROGRAM_CHOICES, blank=True
    )
    student_type = models.CharField(
        max_length=20, choices=STUDENT_TYPE_CHOICES, default='regular'
    )
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    policies_accepted_at = models.DateTimeField(null=True, blank=True)
    policies_version = models.CharField(max_length=20, blank=True, default='')

    class Meta:
        db_table = 'clients'
        ordering = ['full_name']

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    def __str__(self) -> str:
        return self.full_name


class Appointment(models.Model):
    DEVICE_ANDROID = 'android'
    DEVICE_IPHONE = 'iphone'
    DEVICE_LAPTOP = 'laptop'
    DEVICE_CHOICES = [
        (DEVICE_ANDROID, 'Android Phone'),
        (DEVICE_IPHONE, 'iPhone'),
        (DEVICE_LAPTOP, 'Laptop'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_DECLINED = 'declined'
    STATUS_PARTS_UNAVAILABLE = 'parts_unavailable'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_PARTS_UNAVAILABLE, 'Rejected - Parts unavailable'),
        (STATUS_DECLINED, 'Declined - Unsupported'),
    ]

    PAYMENT_GCASH = 'gcash'
    PAYMENT_PERSONAL = 'personal'
    PAYMENT_CHOICES = [
        (PAYMENT_GCASH, 'GCash (contactless)'),
        (PAYMENT_PERSONAL, 'Personal / cash meet-up'),
    ]

    SERVICE_CHOICES = {
        DEVICE_ANDROID: [
            ('lcd', 'LCD replacement'),
            ('amoled', 'AMOLED replacement'),
            ('back_cover', 'Back cover replacement'),
            ('camera', 'Camera module replacement'),
            ('speaker', 'Speaker replacement'),
            ('buttons', 'Button replacement'),
            ('sub_board', 'Sub-board replacement'),
            ('frame', 'Frame replacement'),
        ],
        DEVICE_IPHONE: [
            ('lcd', 'LCD replacement'),
            ('amoled', 'AMOLED replacement'),
            ('back_cover', 'Back cover replacement'),
            ('camera', 'Camera module replacement'),
            ('speaker', 'Speaker replacement'),
            ('buttons', 'Button replacement'),
            ('sub_board', 'Sub-board replacement'),
            ('frame', 'Frame replacement'),
        ],
        DEVICE_LAPTOP: [
            ('laptop_lcd', 'Laptop LCD replacement'),
            ('keyboard', 'Keyboard replacement'),
            ('ram', 'RAM upgrade'),
            ('storage', 'SSD / HDD replacement'),
            ('fan', 'Fan replacement'),
            ('thermal', 'Thermal repaste (no soldering)'),
            ('frame', 'Palm rest / frame replacement'),
            ('io_board', 'Sub-board / IO board swap'),
        ],
    }

    SERVICE_PRICING = {
        DEVICE_ANDROID: {
            'lcd': 600,
            'amoled': 1300,
            'back_cover': 300,
            'camera': 1000,
            'speaker': 700,
            'buttons': 500,
            'sub_board': 200,
            'frame': 900,
        },
        DEVICE_IPHONE: {
            'lcd': 800,
            'amoled': 1500,
            'back_cover': 1400,
            'camera': 3000,
            'speaker': 1300,
            'buttons': 1000,
            'sub_board': 500,
            'frame': 1000,
        },
        DEVICE_LAPTOP: {
            'laptop_lcd': 2100,
            'keyboard': 2000,
            'ram': 1150,
            'storage': 1500,
            'fan': 1100,
            'thermal': 500,
            'frame': 2000,
            'io_board': 2600,
        },
    }

    MODEL_SUGGESTIONS = {
        DEVICE_ANDROID: {
            'samsung': [
                'Galaxy S24 Ultra',
                'Galaxy S24+',
                'Galaxy S24',
                'Galaxy S23 FE',
                'Galaxy S23',
                'Galaxy Z Flip 6',
                'Galaxy Z Fold 6',
                'Galaxy Z Flip 5',
                'Galaxy Z Fold 5',
                'Galaxy A55',
                'Galaxy A54',
                'Galaxy A53',
                'Galaxy A52s 5G',
                'Galaxy A52',
                'Galaxy A35',
                'Galaxy A34',
                'Galaxy A33',
                'Galaxy A32',
                'Galaxy A25',
                'Galaxy A24',
                'Galaxy A23',
                'Galaxy A15 5G',
                'Galaxy A14 5G',
                'Galaxy A13',
                'Galaxy A05s',
                'Galaxy A05',
                'Galaxy A07',
                'Galaxy M55',
                'Galaxy M34',
                'Galaxy C55',
                'Galaxy Xcover 6 Pro',
            ],
            'xiaomi': [
                'Xiaomi 14 Ultra',
                'Xiaomi 14',
                'Xiaomi 13T',
                'Redmi Note 13 Pro+',
                'Redmi Note 13 Pro',
                'Redmi Note 13',
                'Redmi Note 15 Pro+',
                'Redmi Note 15 Pro',
                'Redmi Note 15',
                'Redmi Note 14 Pro+',
                'Redmi Note 14 Pro',
                'Redmi Note 14',
                'Redmi Note 14 SE 5G',
                'Redmi Note 13 SE',
                'Redmi Note 12 Pro+',
                'Redmi Note 12 Pro',
                'Redmi Note 12',
                'Redmi Note 11 Pro+',
                'Redmi Note 11 Pro',
                'Redmi Note 11',
                'Redmi Note 10 Pro',
                'Redmi Note 10',
                'Redmi Note 9 Pro',
                'Redmi Note 9',
                'Redmi Note 8 Pro',
                'Redmi Note 8',
                'Redmi Note 7',
                'Redmi Note 6 Pro',
                'Redmi Note 5 Pro',
                'Redmi A3',
                'Redmi A2 Plus',
                'Redmi A2',
                'Redmi A1',
                'Redmi 15C',
                'Redmi 15C 8+256 Midnight Gray',
                'Redmi 15C (8GB/256GB)',
                'Redmi 14C',
                'Redmi 13C 5G',
                'Redmi 13C',
                'Redmi 12C',
                'Redmi 12',
                'Redmi 10C',
                'Redmi 10',
                'Redmi 9T',
                'Redmi 9 Power',
                'Redmi 9i',
                'Redmi 9A',
                'Redmi 8A',
                'Redmi 8',
                'Redmi 7A',
                'Redmi 6 Pro',
                'Redmi 6A',
                'Redmi 6',
                'Redmi 5A',
                'Redmi 5',
                'Poco X6 Pro',
                'Poco F6 Pro',
                'Poco F6',
                'Poco C65',
                'Xiaomi 12 Lite',
            ],
            'oppo': [
                'Find X7 Ultra',
                'Find X7',
                'Find N3',
                'Find N3 Flip',
                'Find X6 Pro',
                'Find X6',
                'Reno12 Pro',
                'Reno12',
                'Reno11 Pro',
                'Reno11 F',
                'Reno10 Pro+',
                'Reno10 Pro',
                'Reno10',
                'Reno9 Pro',
                'A3 Pro 5G',
                'A3x',
                'A2 Pro',
                'A2x',
                'A98 5G',
                'A79 5G',
                'A78 5G',
                'A77s',
                'A77',
                'A59',
                'A58',
                'A57',
                'A57s',
                'A17',
                'A17k',
                'A16',
                'A16k',
                'A15',
                'C55',
                'C51',
            ],
            'vivo': [
                'X100 Pro+',
                'X100 Pro',
                'X100',
                'X90 Pro+',
                'X90 Pro',
                'X90',
                'X80 Pro',
                'X80',
                'V30 Pro',
                'V30',
                'V29e',
                'V29',
                'V27e',
                'V25 Pro',
                'V25',
                'Y200',
                'Y100',
                'Y78',
                'Y76 5G',
                'Y36',
                'Y27s',
                'Y27',
                'Y22s',
                'Y18',
                'Y17s',
                'Y16',
                'Y02s',
                'iQOO 12',
                'iQOO 12 Pro',
                'iQOO 11S',
                'iQOO 11',
                'iQOO Neo9 Pro',
                'iQOO Neo9',
                'iQOO Neo8',
                'iQOO Z9x',
                'iQOO Z8x',
            ],
            'realme': [
                'Realme C3',
                'Realme C15',
                'Realme C25',
                'Realme C25Y',
                'Realme C30',
                'Realme C31',
                'Realme C33',
                'Realme C35',
                'Realme C61',
                'Realme C63',
                'Realme C65',
                'Realme C67',
                'Realme C71',
                'Realme C75',
                'Realme C75X',
                'Realme C85 4G',
                'Realme C85 5G',
                'Realme 1',
                'Realme 2',
                'Realme 2 Pro',
                'Realme 5',
                'Realme 5 Pro',
                'Realme 6',
                'Realme 6i',
                'Realme 7',
                'Realme 7i',
                'Realme 8',
                'Realme 8 5G',
                'Realme 9',
                'Realme 9i',
                'Realme 9 Pro 5G',
                'Realme 9 Pro+ 5G',
                'Realme 10',
                'Realme 10 Pro+',
                'Realme 11',
                'Realme 12',
                'Realme 12 5G',
                'Realme 12 Plus 5G',
                'Realme 12 Pro 5G',
                'Realme 12 Pro+ 5G',
                'Realme 13',
                'Realme 13 5G',
                'Realme 13+ 5G',
                'Realme 13 Pro 5G',
                'Realme 13 Pro+ 5G',
                'Realme 14',
                'Realme 14 5G',
                'Realme 14 Pro',
                'Realme 14 Pro+ 5G',
                'Realme 15',
                'Realme 15 5G',
                'Realme 15 Pro',
                'Realme 15T 5G',
                'Realme 16 Pro+ 5G',
                'Realme XT',
                'Realme X',
                'Realme X2',
                'Realme X2 Pro',
                'Realme X3',
                'Realme X3 SuperZoom',
                'Realme GT',
                'Realme GT 2 Pro',
                'Realme GT 3',
                'Realme GT 5',
                'Realme GT 5 Pro',
                'Realme GT 6T',
                'Realme GT 7',
                'Realme GT 7T',
                'Realme GT 8 Pro',
                'Realme GT Neo 2',
                'Realme GT Neo 3',
                'Realme GT Neo 5',
                'Realme GT Neo 6',
                'Realme Narzo 10',
                'Realme Narzo 10A',
                'Realme Narzo 20',
                'Realme Narzo 20A',
                'Realme Narzo 30',
                'Realme Narzo 30A',
                'Realme Narzo 30 Pro',
                'Realme Narzo 50',
                'Realme Narzo 50A',
                'Realme Narzo 50A Prime',
                'Realme Narzo 50i',
                'Realme Narzo 50 Pro',
                'Realme Narzo 60',
                'Realme Narzo 60 Pro',
                'Realme Narzo 70',
                'Realme Narzo 70 Pro',
                'Realme Narzo 70 5G',
                'Realme Narzo 70 Pro 5G',
                'Realme Narzo 90',
                'Realme Narzo 90 Pro',
                'Realme Narzo 90x',
                'Realme Narzo N50',
                'Realme Narzo N53',
                'Realme Narzo N55',
                'Realme Narzo C51',
                'Realme Narzo C55',
            ],
            'oneplus': ['OnePlus 12', 'OnePlus 12R', 'Nord CE 4', 'OnePlus 11R', 'Nord N30', 'OnePlus Ace 3', 'Nord 3'],
            'huawei': ['Nova 12i', 'P60 Pro', 'Mate 50', 'Y9a', 'Nova 11i', 'Mate X3'],
            'honor': ['Magic6 Pro', 'X9b', 'Magic Vs', 'X7a', '90 Lite', 'Magic5 Pro'],
            'motorola': ['Edge 40', 'Moto G Stylus', 'Razr 40 Ultra', 'Moto G54', 'Edge 30 Neo', 'Moto G Power 5G'],
            'nokia': ['G60', 'XR21', 'C32', 'X30', 'G310', 'C12 Pro'],
            'asus': ['ROG Phone 8', 'Zenfone 10', 'ROG Phone 7', 'Zenfone 9'],
            'sony': ['Xperia 1 V', 'Xperia 5 V', 'Xperia 10 V', 'Xperia 1 IV'],
            'lg': ['Wing', 'Velvet', 'V60 ThinQ'],
            'tecno': [
                'Tecno 10A',
                'Tecno T101',
                'Tecno T301',
                'Tecno T302',
                'Tecno T313',
                'Tecno T372N',
                'Tecno T402',
                'Tecno T454',
                'Tecno T475',
                'Tecno C5',
                'Tecno C5S',
                'Tecno C7',
                'Tecno C8',
                'Tecno C9',
                'Tecno C9S',
                'Camon CM (CA6S)',
                'Camon CA8',
                'Camon 11',
                'Camon 11 Pro',
                'Camon 12 Air (CC6)',
                'Camon 12 (CC7)',
                'Camon 12 Pro (CC9)',
                'Camon 15 Air (CD6)',
                'Camon 15 (CD7)',
                'Camon 15 Pro (CD8)',
                'Camon 15 Premier (CD8j)',
                'Camon 16 (CE7)',
                'Camon 16 Pro (CE8)',
                'Camon 16 Premier (CE9h)',
                'Camon 17',
                'Camon 17P',
                'Camon 17 Pro',
                'Camon 18',
                'Camon 18P',
                'Camon 18T',
                'Camon 18 Premier',
                'Camon 19',
                'Camon 19 Neo',
                'Camon 20',
                'Camon 20 Pro',
                'Camon 20 Pro 5G',
                'Camon 20 Premier 5G',
                'Camon 30',
                'Camon 30 5G',
                'Camon 30 Pro 5G',
                'Camon 30 Premier 5G',
                'Pova Neo',
                'Pova 3',
                'Pova 4',
                'Pova 5G',
                'Pova 6',
                'Pova 6 Neo',
                'Pova 6 Pro',
                'Pova 6 Pro 5G',
                'Pova 7',
                'Pova 7 5G',
                'Spark 8',
                'Spark 8C',
                'Spark 8 Pro',
                'Spark 10',
                'Spark 10C',
                'Spark 10 Pro',
                'Spark 10 5G',
                'Spark 20C',
                'Spark 20',
                'Spark 20 Pro',
                'Spark 20 Pro+',
                'Spark 30',
                'Spark 30 Pro',
                'Spark 40',
                'Spark 40 Pro',
                'Spark 40 Pro+',
                'Spark Go 2',
                'Spark Go 2024',
                'Spark 5',
                'Spark 6',
                'Spark 7',
                'Phantom X',
                'Phantom X2',
                'Phantom V Flip',
                'Phantom V Fold2 5G',
                'Phantom V Flip2 5G',
                'Phantom Ultimate G Fold',
                'Tecno Pop 5',
                'Tecno Pop 5 LTE',
                'Tecno Go 2020',
                'Tecno Go 2',
            ],
            'itel': [
                'P55 5G',
                'P55+',
                'P40+',
                'P40',
                'P38 Pro',
                'C55',
                'C23',
                'C20',
                'C30',
                'S24 Ultra',
                'S24',
                'S23+',
                'S23',
                'S23 Pro',
            ],
            'infinix': [
                'Zero 30',
                'Zero 5G 2024',
                'Zero Ultra',
                'Zero 5G',
                'Note 60 Pro',
                'Note 60',
                'Note 60 5G',
                'Note 50',
                'Note 50 Pro',
                'Note 40',
                'Note 40 Pro+',
                'Note 40 5G',
                'Note 30',
                'Note 30 VIP',
                'Note 12 G96',
                'Hot 60 Pro',
                'Hot 60',
                'Hot 40 Pro',
                'Hot 40i',
                'Hot 30i',
                'Hot 20S',
                'Hot 12 Play',
                'Hot 11S',
                'Hot 10',
                'Smart 5',
                'Smart 5 Pro',
                'Smart 6',
                'Smart 6 HD',
                'Smart 6 Plus',
                'Smart 7',
                'Smart 7 Plus',
                'Smart 7 HD',
                'Smart 8',
                'Smart 8 Plus',
                'Smart 9',
                'Smart 9 HD',
                'Smart 10',
                'Smart 10 Plus',
                'GT 30 Pro',
                'GT 30',
                'GT 10 Pro',
                'GT 20 Pro',
            ],
            'zte': ['Axon 50', 'RedMagic 9 Pro', 'Axon 40', 'RedMagic 8'],
            'meizu': ['Meizu 21', '18s Pro', '20 Infinity'],
            'poco': [
                'Poco F8 Ultra',
                'Poco F8',
                'Poco F7 Pro',
                'Poco F7',
                'Poco F6 Pro',
                'Poco F6',
                'Poco F5 Pro',
                'Poco F5',
                'Poco F4 GT',
                'Poco F4',
                'Poco F3',
                'Poco F2 Pro',
                'Poco F1',
                'Poco X7 Pro',
                'Poco X7',
                'Poco X6 Pro',
                'Poco X6',
                'Poco X5 Pro 5G',
                'Poco X5 5G',
                'Poco X4 GT',
                'Poco X4 Pro 5G',
                'Poco X3 Pro',
                'Poco X3 NFC',
                'Poco X2',
                'Poco M8 Pro 5G',
                'Poco M8 5G',
                'Poco M7 Pro 5G',
                'Poco M7',
                'Poco M6 Pro',
                'Poco M5s',
                'Poco M5',
                'Poco M4 Pro 5G',
                'Poco M4 5G',
                'Poco M3 Pro 5G',
                'Poco M3',
                'Poco M2 Pro',
                'Poco C55',
                'Poco C51',
                'Poco C50',
                'Poco C40',
                'Poco C3',
                'Poco C65',
                'Poco C55s',
                'Poco C35',
                'Poco C25',
                'Poco C20',
            ],
            'panasonic': ['Eluga I8', 'Eluga X1'],
            'sharp': ['Aquos R7', 'Aquos Sense8'],
            'blackview': ['BV9800 Pro', 'BV9200', 'N6000'],
            'doogee': ['S100 Pro', 'V30', 'Smini'],
            'cat': ['Cat S75', 'Cat S62 Pro'],
            'fairphone': ['Fairphone 5', 'Fairphone 4'],
            'kyocera': ['DuraForce Ultra 5G', 'DuraSport 5G'],
            'lava': ['Agni 2', 'Blaze 2', 'Yuva 3 Pro'],
            'micromax': ['In 2c', 'In Note 2'],
            'iqoo': ['iQOO 12', 'iQOO Neo 9 Pro', 'iQOO Z7'],
            'cubot': ['Pocket 3', 'KingKong Star'],
            'ulefone': ['Power Armor 18T', 'Armor 24'],
        },
        DEVICE_IPHONE: {
            'apple': [
                'iPhone 15 Pro Max',
                'iPhone 15 Pro',
                'iPhone 15',
                'iPhone 14 Pro',
                'iPhone 14',
                'iPhone 13',
                'iPhone 13 mini',
                'iPhone 12',
                'iPhone SE (3rd Gen)',
                'iPhone 11',
                'iPhone XR',
                'iPhone XS',
                'iPhone X',
                'iPhone 7',
                'iPhone 6s',
                'iPhone 6',
            ],
        },
        DEVICE_LAPTOP: {
            'acer': [
                'Aspire 3',
                'Aspire 5',
                'Aspire 7',
                'Aspire Go',
                'Aspire Go Spin',
                'Aspire Vero',
                'Swift 14',
                'Swift 16',
                'Swift Go 14',
                'Swift Go 16',
                'Nitro 5',
                'Nitro V 15',
                'Nitro 16',
                'Nitro 17',
                'Predator Helios 16',
                'Predator Helios 18',
                'Predator Triton 14',
                'Predator Triton 17X',
                'TravelMate P4',
                'TravelMate P6',
                'TravelMate classic',
                'Extensa 14',
                'Extensa 15',
                'Acer Chromebook 311',
                'Acer Chromebook 314',
                'Acer Chromebook 315',
                'Chromebook Spin 314',
                'Chromebook Spin 512',
                'Chromebook Plus 515',
                'Acer One 10',
                'Aspire One',
                'Aspire Timeline',
                'Aspire TimelineX',
            ],
            'asus': [
                'Zenbook 13',
                'Zenbook 14',
                'Zenbook 15',
                'Zenbook S 14',
                'Zenbook S 16',
                'Zenbook Duo',
                'Zenbook Pro Duo',
                'Vivobook Go 15',
                'Vivobook Classic 16',
                'Vivobook S 15',
                'Vivobook Pro 16X',
                'Vivobook Flip 14',
                'Vivobook Flip 16',
                'Vivobook Gaming 16X',
                'ROG Zephyrus G14',
                'ROG Zephyrus G16',
                'ROG Zephyrus Duo',
                'ROG Strix G18',
                'ROG Strix Scar 16',
                'ROG Flow X13',
                'ROG Flow Z13',
                'TUF Gaming A15',
                'TUF Gaming F16',
                'ProArt StudioBook 16',
                'ProArt StudioBook Pro X',
                'ExpertBook B9',
                'ExpertBook B5',
                'ASUS Chromebook CX34',
                'ASUS Chromebook Flip',
                'EeeBook X205',
                'ASUSPRO B9440',
                'ASUS G Series',
                'ASUS X Series',
                'ASUS N Series',
                'ASUS K Series',
                'ASUS V Series',
                'ASUS F Series',
                'ASUS A Series',
                'ASUS Q Series',
                'ASUS U Series',
            ],
            'dell': [
                'Inspiron 11 3195',
                'Inspiron 13 7300',
                'Inspiron 14 5402',
                'Inspiron 15 3520',
                'Inspiron 16 5630',
                'Inspiron 17 7730',
                'Inspiron 15 3511',
                'Inspiron 15 3530',
                'Inspiron 14 7420',
                'Inspiron 13 5310',
                'G3 15 3500',
                'G3 15 3590',
                'G5 15 5500',
                'G5 15 5590',
                'G7 15 7500',
                'G7 17 7700',
                'Precision 3551',
                'Precision 5550',
                'Precision 7560',
                'Precision 7770',
                'Alienware m15 R6',
                'Alienware m17 R5',
                'Alienware x15 R2',
                'Alienware x17 R2',
                'Chromebook 11 3100',
                'Chromebook 13 3380',
                'Chromebook 14 3420',
            ],
            'hp': [
                'HP 14-ck0010',
                'HP 14-dw1000',
                'HP 15-EF0021',
                'HP 15-FR0023',
                'Victus 15-fa0031',
                'Victus 15-fb1007',
                'Omen 15-dx1075',
                'Omen 16-b1000',
                'Omen X 2S',
                'Spectre x360 13-aw2000',
                'Spectre x360 14-ef0000',
                'Spectre x360 15-eb1000',
                'Envy x360 13-bf0000',
                'Envy x360 15-ey0000',
                'ProBook 430 G9',
                'ProBook 440 G10',
                'ProBook 450 G10',
                'ProBook 645 G9',
                'EliteBook 830 G10',
                'EliteBook 840 G10',
                'EliteBook 850 G10',
                'EliteBook x360 1030 G8',
                'EliteBook x360 1040 G8',
                'ZBook Firefly 14 G10',
                'ZBook Power G10',
                'ZBook Studio G10',
                'ZBook Fury 17 G10',
                'HP Chromebook 14a',
                'HP Chromebook x2 11',
            ],
            'lenovo': [
                'ThinkPad T14 Gen 4',
                'ThinkPad T14s Gen 4',
                'ThinkPad T15 Gen 2',
                'ThinkPad X1 Carbon Gen 11',
                'ThinkPad X1 Yoga Gen 8',
                'ThinkPad X1 Nano',
                'ThinkPad X13 Gen 4',
                'ThinkPad X13 Yoga Gen 4',
                'ThinkPad P14s Gen 4',
                'ThinkPad P16 Gen 2',
                'ThinkPad P1 Gen 6',
                'ThinkPad L14 Gen 4',
                'ThinkPad E14 Gen 5',
                'ThinkBook 13s Gen 4',
                'ThinkBook 14 Gen 6',
                'ThinkBook 15 Gen 5',
                'IdeaPad 1 14',
                'IdeaPad 3 15',
                'IdeaPad 5 Pro 14',
                'IdeaPad 7 16',
                'IdeaPad Flex 5 14',
                'IdeaPad Slim 5',
                'IdeaPad Slim 7',
                'Legion 5 Pro 16',
                'Legion 7 16',
                'Legion Slim 7',
                'Yoga 6',
                'Yoga 7i',
                'Yoga 9i',
                'Lenovo Chromebook Duet',
                'Chromebook Flex 5',
                'IdeaPad Chromebook 3',
            ],
            'msi': ['Stealth 16 Studio', 'Raider GE78', 'Cyborg 15', 'Modern 14'],
            'razer': ['Blade 16', 'Blade 18', 'Blade 15', 'Blade Stealth 13'],
            'gigabyte': ['Aero 16', 'Aorus 17', 'G5 KF', 'Aero 14'],
            'samsung': ['Galaxy Book4 Pro', 'Galaxy Book3', 'Galaxy Book2 360', 'Galaxy Book Flex2'],
            'huawei': ['MateBook X Pro', 'MateBook D16', 'MateBook 14s', 'MateBook D15'],
            'lg': ['Gram 17', 'Gram SuperSlim', 'Gram Style', 'Gram 16 2-in-1'],
            'microsoft': ['Surface Laptop 6', 'Surface Laptop Studio 2', 'Surface Go 4', 'Surface Pro 9'],
            'framework': ['Framework Laptop 13', 'Framework Laptop 16'],
            'alienware': ['x16 R2', 'm18 R2', 'x14', 'x14 R2'],
            'acerpredator': ['Predator Helios 300', 'Triton 17 X', 'Helios Neo 16'],
            'evga': ['EVGA SC17'],
            'dynabook': ['Tecra A40', 'Portégé X40'],
            'fujitsu': ['Lifebook U9313', 'UH-X'],
            'chuwi': ['GemiBook Plus', 'Hi10 X Pro'],
            'xpg': ['XPG Xenia 15', 'Xenia 16 Pro'],
            'avita': ['Liber V14', 'Essential 14'],
        },
    }

    BRAND_CHOICES = {
        DEVICE_ANDROID: [
            ('samsung', 'Samsung'),
            ('google', 'Google Pixel'),
            ('xiaomi', 'Xiaomi'),
            ('oppo', 'OPPO'),
            ('vivo', 'Vivo'),
            ('realme', 'Realme'),
            ('oneplus', 'OnePlus'),
            ('huawei', 'Huawei'),
            ('honor', 'HONOR'),
            ('motorola', 'Motorola'),
            ('nokia', 'Nokia'),
            ('nothing', 'Nothing'),
            ('lenovo', 'Lenovo'),
            ('asus', 'ASUS'),
            ('sony', 'Sony Xperia'),
            ('lg', 'LG'),
            ('tecno', 'Tecno'),
            ('infinix', 'Infinix'),
            ('itel', 'Itel'),
            ('zte', 'ZTE'),
            ('meizu', 'Meizu'),
            ('poco', 'POCO'),
            ('panasonic', 'Panasonic'),
            ('sharp', 'Sharp'),
            ('blackview', 'Blackview'),
            ('doogee', 'Doogee'),
            ('cat', 'Cat'),
            ('fairphone', 'Fairphone'),
            ('kyocera', 'Kyocera'),
            ('lava', 'Lava'),
            ('micromax', 'Micromax'),
            ('iqoo', 'iQOO'),
            ('cubot', 'Cubot'),
            ('ulefone', 'Ulefone'),
            ('other', 'Other / not listed'),
        ],
        DEVICE_IPHONE: [
            ('apple', 'Apple'),
        ],
        DEVICE_LAPTOP: [
            ('acer', 'Acer'),
            ('asus', 'ASUS'),
            ('dell', 'Dell'),
            ('hp', 'HP'),
            ('lenovo', 'Lenovo'),
            ('msi', 'MSI'),
            ('razer', 'Razer'),
            ('gigabyte', 'Gigabyte'),
            ('samsung', 'Samsung'),
            ('huawei', 'Huawei'),
            ('lg', 'LG'),
            ('microsoft', 'Microsoft Surface'),
            ('framework', 'Framework'),
            ('alienware', 'Alienware'),
            ('acerpredator', 'Acer Predator'),
            ('evga', 'EVGA'),
            ('dynabook', 'Dynabook'),
            ('fujitsu', 'Fujitsu'),
            ('chuwi', 'Chuwi'),
            ('xpg', 'XPG / Tongfang'),
            ('avita', 'Avita'),
            ('other', 'Other / not listed'),
        ],
    }

    LOCATION_CHOICES = [
        ('meetup-central', 'Central meetup lounge'),
        ('meetup-east', 'East transit meetup point'),
        ('meetup-tech', 'Tech plaza drop-off counter'),
    ]

    client = models.ForeignKey(
        ClientAccount,
        on_delete=models.SET_NULL,
        related_name='appointments',
        null=True,
        blank=True,
    )
    appointment_id = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=150)
    contact_number = models.CharField(max_length=30)
    notification_email = models.EmailField(blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_CHOICES)
    device_brand = models.CharField(max_length=50, default='samsung')
    brand_model = models.CharField(max_length=150)
    service_type = models.CharField(max_length=50)
    issue_description = models.TextField()
    preferred_datetime = models.DateTimeField()
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)
    location_notes = models.CharField(max_length=120, blank=True)
    proof_image = models.ImageField(upload_to='appointment_proofs/', blank=True, null=True)
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default=PAYMENT_PERSONAL
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    admin_notes = models.TextField(blank=True)
    parts_ordered = models.BooleanField(default=False)
    policies_accepted_at = models.DateTimeField(null=True, blank=True)
    policies_version = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.full_name} • {self.service_label}"

    @property
    def masked_tracking_number(self) -> str:
        if not self.appointment_id:
            return ''
        return f"{self.appointment_id[:3]}•••{self.appointment_id[-2:]}"

    @property
    def masked_id(self) -> str:
        if len(self.appointment_id) <= 4:
            return '•••'
        return f"{self.appointment_id[:4]}••••{self.appointment_id[-2:]}"

    @property
    def service_label(self) -> str:
        for opts in self.SERVICE_CHOICES.values():
            for value, label in opts:
                if value == self.service_type:
                    return label
        return self.service_type

    @property
    def brand_label(self) -> str:
        for opts in self.BRAND_CHOICES.values():
            for value, label in opts:
                if value == self.device_brand:
                    return label
        return self.device_brand

    def clean(self):
        unsupported_keywords = ['solder', 'board level', 'motherboard', 'logic board', 'reball']
        description_lower = self.issue_description.lower()
        if any(keyword in description_lower for keyword in unsupported_keywords):
            raise ValidationError('Board-level or soldering repairs are not accepted.')

        if self.device_type == self.DEVICE_IPHONE and 'battery' in description_lower:
            raise ValidationError('iPhone battery issues are not accepted.')

        if self.device_type == self.DEVICE_IPHONE and self.service_type == 'battery':
            raise ValidationError('iPhone battery services are not available.')

        allowed_codes = {value for value, _ in self.SERVICE_CHOICES.get(self.device_type, [])}
        if self.service_type not in allowed_codes:
            raise ValidationError('Selected service is not available for this device type.')

        allowed_brands = {value for value, _ in self.BRAND_CHOICES.get(self.device_type, [])}
        if self.device_type == self.DEVICE_IPHONE:
            self.device_brand = 'apple'
        elif self.device_brand not in allowed_brands:
            raise ValidationError('Select a supported brand for this device type.')

        if self.device_brand and self.device_type in self.MODEL_SUGGESTIONS:
            brand_models = self.MODEL_SUGGESTIONS[self.device_type].get(self.device_brand, [])
            if brand_models:
                normalized = self.brand_model.replace('-', ' ').lower()
                is_known = any(m.replace('-', ' ').lower() == normalized for m in brand_models)
                if not is_known:
                    suggestions = ', '.join(brand_models[:4])
                    raise ValidationError(
                        f'Please specify a known model for {self.device_brand.title()}. '
                        f'Examples: {suggestions}'
                    )


    def save(self, *args, **kwargs):
        if not self.appointment_id:
            today_str = timezone.now().strftime('%y%m%d')
            unique_segment = get_random_string(4).upper()
            self.appointment_id = f'BIP-{today_str}-{unique_segment}'
        super().save(*args, **kwargs)

    @property
    def service_price(self) -> int:
        return self.SERVICE_PRICING.get(self.device_type, {}).get(self.service_type, 0)

    @property
    def is_management_locked(self) -> bool:
        hard_lock_statuses = {
            self.STATUS_COMPLETED,
            self.STATUS_PARTS_UNAVAILABLE,
            self.STATUS_DECLINED,
        }
        if self.status in hard_lock_statuses:
            return True
        return self.status == self.STATUS_APPROVED and self.parts_ordered


class ContactMessage(models.Model):
    PREFERRED_CHOICES = [
        ('sms', 'SMS / Viber'),
        ('email', 'Email'),
        ('messenger', 'Messenger / Chat'),
    ]
    STATUS_OPEN = 'open'
    STATUS_IN_REVIEW = 'in_review'
    STATUS_RESOLVED = 'resolved'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_REVIEW, 'In review'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    client = models.ForeignKey(
        ClientAccount, on_delete=models.CASCADE, related_name='contact_messages'
    )
    subject = models.CharField(max_length=120)
    body = models.TextField()
    preferred_contact = models.CharField(
        max_length=20, choices=PREFERRED_CHOICES, default='sms'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    admin_reply = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact_messages'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.subject} - {self.client.full_name}'


class ContactMessageReply(models.Model):
    AUTHOR_ADMIN = 'admin'
    AUTHOR_CHOICES = [(AUTHOR_ADMIN, 'Admin Crew')]

    message = models.ForeignKey(
        ContactMessage,
        on_delete=models.CASCADE,
        related_name='replies',
    )
    author = models.CharField(max_length=20, choices=AUTHOR_CHOICES, default=AUTHOR_ADMIN)
    admin = models.ForeignKey(
        AdminUser,
        on_delete=models.SET_NULL,
        related_name='message_replies',
        null=True,
        blank=True,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'contact_message_replies'
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'Reply to {self.message_id} at {self.created_at:%Y-%m-%d %H:%M}'

    @staticmethod
    def _initials_from_name(name: str | None, fallback: str = 'RC') -> str:
        if not name:
            return fallback
        parts = [part[0] for part in name.split() if part]
        return ''.join(parts[:2]).upper() or fallback

    @property
    def display_admin_name(self) -> str:
        if self.admin and self.admin.full_name:
            return self.admin.full_name
        return 'Repair Crew'

    @property
    def display_admin_initials(self) -> str:
        name = self.admin.full_name if self.admin and self.admin.full_name else None
        return self._initials_from_name(name)
