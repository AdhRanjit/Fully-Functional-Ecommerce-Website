# Brand T:

Brand T is a streamlined e-commerce website designed and developed by Ranjit Adhikari and Simon Newcomb as part of their Software Engineering project.The website focuses on delivering a simple and genuine shopping experience by featuring products from a single, verified seller. With an emphasis on clean UX/UI design, Brand T aims to provide customers with a trustworthy platform for their online purchases whilemaintaining ease of use and efficiency.

## Key Features:

- **Single Seller**: Only one verified seller provides products on the platform, ensuring authenticity.
- **Admin Panel**: Full administrative control to manage products, categories, orders, and customer information.
- **Product Listings**: Easy-to-manage product pages with pricing, descriptions, and image support.
- **Customer Accounts**: Customers can create accounts, manage their orders, and view their purchase history.
- **Secure Payments with Stripe**: Customers can securely pay for their orders via Stripe, a popular payment gateway.

  ## Technologies Used:

- **Python**: The core backend programming language used to build the application logic.
- **Django**: A high-level Python web framework used for rapid development of the e-commerce platform.
- **HTML/CSS**: Used for designing and styling the frontend of the application, ensuring a responsive and user-friendly interface.
- **JavaScript**: Used for interactive elements and enhancing user experience on the frontend.
- **Stripe**: A secure payment gateway integrated to handle customer transactions and payments.
- **SQLite**: A lightweight, file-based database used for storing application data like user accounts, orders, and product information.


## Setup instruction
Follow the steps below to set up and run your BrandT Django e-commerce Project.

### Step 1: Open Code in Visual Studio(Optional)
Open the code in Visual Studio, and make sure you have the **.env** files configured. Open that file and fill your information.
> EMAIL_HOST_USER => your gmail id
> EMAIL_HOST_PASSWORD => password for gmail
> STRIPE_PUBLIC => stripe public key
> STRIPE_PRIVATE => stripe private key

**Open templates/account/cart.html**
 Add your public key inside Stripe('')

### Step 2: Open PowerShell
> Open Powershell from the Start menu.

### Step 3: Navigate to Your Project Directory
Change the directory to where your Django project is located using the cd command:
> cd path\to\your\project

### Step 4: Remove Existing Virtual Environment
If you download the project, it will have virtual environment. Delete virtual environment (venv) file from the Folder or enter this command.

> Remove-Item -Recurse -Force .\venv\

#### Note: Make sure there is no venv file in your folder. Use ls to check.

### Step 5: Install virtual environment in your system.
pip install virtualenv

### Step 6: Create a New Virtual Environment
Create a new virtual environment in your project directory
> virtualenv venv

### Step 7: Activate the virtual Environment
Activate the virtual environment.
> .\venv\Scripts\Activate.ps1

### Step 8: Install Dependencies
Install all required packages from the requirements.txt file
> pip install -r requirements.txt

### Step 9: Run Migrations
Run migrations for your Django apps:
> python manage.py makemigrations
> python manage.py migrate
> python manage.py makemigrations home
> python manage.py migrate
> python manage.py makemigrations products
> python manage.py migrate
> python manage.py makemigrations accounts
> python manage.py migrate

#### Note: otherwise you can directly type: 
> python manage.py makemigrations; python manage.py migrate; python manage.py makemigrations home; python manage.py migrate; python manage.py makemigrations products; python manage.py migrate; python manage.py makemigrations accounts; python manage.py migrate

### Step 10: Create a Superuser
Create an admin superuser to manage your site:
> python manage.py createsuperuser
#### Enter your details when prompted.

### Step 11: Set Up Site Configuration
Open the Django shell:
> python manage.py shell

**Configure the domain and name for the site:**
> from django.contrib.sites.models import Site
> site = Site.objects.get(id=1)
> site.domain = 'localhost:8000'  # Replace with your domain
> site.name = 'BrandT'            # Set the site name
> site.save()
> exit()

### Step 12: Run your server
> python manage.py runserver

### Step 13: Open Google Chrome
After your open chrome. Enter this detail to open the site:
**User**
> http://127.0.0.1:8000/

**Admin**
> http://127.0.0.1:8000/admin/

**Username is admin and password is admin.**
**If you created your own then you might have your own username and password.**

### For Payment Process:
Follow the instruction as per Stripe Policy. One of the instruction is:
> Default card no. for stripe is 4242.......42 and, date and cvv can be anything

**After running the file, if you want to run again later, you dont have to do it again:
follow this steps:**
For my project: C:\Users\rjadh\OneDrive\Desktop\Program\SE_Project\Project\Client>
(Powershell)
1. Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
2. .\venv\Scripts\Activate
3. python manage.py runserver
4. open http://127.0.0.1:8000/ in website for website
5. http://127.0.0.1:8000/admin/login/?next=/admin/ to login admin page

Youtube Video: Will posted very soon!
