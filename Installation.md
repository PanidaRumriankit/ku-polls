1. Clone or download the code from Github <br>
    `git clone https://github.com/PanidaRumriankit/ku-polls`
2. Create a virtual environment <br>
    `python -m venv venv`
3. Activate the virtual environment <br>
    `venv\Scripts\activate`
4. Install dependencies <br>
    `pip install -r requirements.txt`
5. Set values for externalized variables <br>
    `cp .env.sample .env`
6. Run migrations <br>
    `python manage.py migrate`
7. Run tests <br>
    `python manage.py test`
8. Install data from the data fixtures <br>
    `python manage.py loaddata data/<filename>`
    
