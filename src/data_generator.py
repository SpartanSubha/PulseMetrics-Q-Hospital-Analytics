"""
PulseMetrics-Q: Hospital Chain Quarterly Analytics
Data Generator Script (v3 — Full Non-Uniform Distribution)
=====================================================
Generates 9 realistic, messy datasets for a pan-India hospital chain.
Run this script once to populate /data/raw/ with all CSVs.

v3 Changes (on top of v2):
  - Monthly admission volume shaped by Indian hospital seasonality (±15% MoM)
  - Weekday-heavy admission dates (weekday:weekend ratio ~1.1:0.75)
  - Hospital "Center of Excellence" department specialization profiles
  - Gender-biased patient selection by department (Gynecology → Female)
  - Revenue seasonality multiplier (charges vary by admission month)
  - Payer-specific discount ranges (Self-Pay 0–5%, Govt 15–25%)
  - Payer × Tier-specific collection rates (Cashless ~93%, Govt ~75%)
  - Variable billing lag (Day-care 0–1d, ICU 2–7d, Tier-2 adds 0–2d)
  - Test-specific lab result distributions (CBC 5% Critical, Troponin 25%)
  - Hospital-correlated food ratings (aligned with CSAT base)
  - Realistic bimodal age distribution (pediatric peak + middle-age bulk)
  - Referral source correlated with insurance type

v2 Changes:
  - Hospital admission volume weighted by bed capacity
  - Revenue varies by hospital tier, region, and department
  - LOS driven by department and diagnosis severity
  - Mortality and readmission linked to severity (not random)
  - CSAT/NPS varies by hospital "personality"
  - Seasonal disease patterns (monsoon infectious spikes)
  - Lab/pharmacy order intensity weighted by ward type
  - Doctor-hospital matching
  - Metro vs Tier-2 payer mix
  - Tier-based stockout rates

Author  : PulseMetrics-Q Portfolio Project
Domain  : Healthcare Analytics
Tables  : dim_hospitals, dim_patients, dim_doctors, dim_icd_codes,
          fact_admissions, fact_billing, fact_lab_orders,
          fact_pharmacy_orders, fact_patient_feedback
"""

import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, timedelta

# ── Reproducibility ──────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Helper utilities ─────────────────────────────────────────────────────────

def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def random_datetime(start: datetime, end: datetime) -> datetime:
    return random_date(start, end)

def save(df: pd.DataFrame, name: str):
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"  [OK] {name}.csv -> {len(df):,} rows | {df.shape[1]} columns")

# ─────────────────────────────────────────────────────────────────────────────
# 1.  DIM_HOSPITALS  (25 rows) — UNCHANGED
# ─────────────────────────────────────────────────────────────────────────────

def generate_dim_hospitals() -> pd.DataFrame:
    hospitals = [
        (1,  "PulseMetrics Hospital Bengaluru",     "Bengaluru",     "Karnataka",       "South", "Tier-1", 650, 2005, "NABH"),
        (2,  "PulseMetrics Hospital Mumbai",         "Mumbai",        "Maharashtra",     "West",  "Tier-1", 800, 2002, "JCI"),
        (3,  "PulseMetrics Hospital Delhi",          "Delhi",         "Delhi",           "North", "Tier-1", 720, 2001, "NABH"),
        (4,  "PulseMetrics Hospital Chennai",        "Chennai",       "Tamil Nadu",      "South", "Tier-1", 600, 2006, "NABH"),
        (5,  "PulseMetrics Hospital Hyderabad",      "Hyderabad",     "Telangana",       "South", "Tier-1", 580, 2008, "NABH"),
        (6,  "PulseMetrics Hospital Pune",           "Pune",          "Maharashtra",     "West",  "Tier-1", 450, 2010, "NABH"),
        (7,  "PulseMetrics Hospital Kolkata",        "Kolkata",       "West Bengal",     "East",  "Tier-1", 500, 2004, "NABH"),
        (8,  "PulseMetrics Hospital Ahmedabad",      "Ahmedabad",     "Gujarat",         "West",  "Tier-1", 420, 2009, "None"),
        (9,  "PulseMetrics Hospital Jaipur",         "Jaipur",        "Rajasthan",       "North", "Tier-2", 320, 2012, "None"),
        (10, "PulseMetrics Hospital Lucknow",        "Lucknow",       "Uttar Pradesh",   "North", "Tier-2", 300, 2013, "None"),
        (11, "PulseMetrics Hospital Bhubaneswar",    "Bhubaneswar",   "Odisha",          "East",  "Tier-2", 280, 2014, "NABH"),
        (12, "PulseMetrics Hospital Chandigarh",     "Chandigarh",    "Punjab",          "North", "Tier-2", 260, 2015, "None"),
        (13, "PulseMetrics Hospital Kochi",          "Kochi",         "Kerala",          "South", "Tier-2", 310, 2011, "NABH"),
        (14, "PulseMetrics Hospital Indore",         "Indore",        "Madhya Pradesh",  "West",  "Tier-2", 240, 2016, "None"),
        (15, "PulseMetrics Hospital Nagpur",         "Nagpur",        "Maharashtra",     "West",  "Tier-2", 220, 2017, "None"),
        (16, "PulseMetrics Hospital Coimbatore",     "Coimbatore",    "Tamil Nadu",      "South", "Tier-2", 200, 2018, "None"),
        (17, "PulseMetrics Hospital Visakhapatnam",  "Visakhapatnam", "Andhra Pradesh",  "South", "Tier-2", 230, 2015, "None"),
        (18, "PulseMetrics Hospital Patna",          "Patna",         "Bihar",           "East",  "Tier-2", 190, 2019, "None"),
        (19, "PulseMetrics Hospital Guwahati",       "Guwahati",      "Assam",           "East",  "Tier-2", 180, 2020, "None"),
        (20, "PulseMetrics Hospital Thiruvananthapuram","Thiruvananthapuram","Kerala",   "South", "Tier-2", 210, 2016, "None"),
        (21, "PulseMetrics Hospital Surat",          "Surat",         "Gujarat",         "West",  "Tier-2", 200, 2018, "None"),
        (22, "PulseMetrics Hospital Vadodara",       "Vadodara",      "Gujarat",         "West",  "Tier-2", 185, 2019, "None"),
        (23, "PulseMetrics Hospital Bhopal",         "Bhopal",        "Madhya Pradesh",  "West",  "Tier-2", 175, 2020, "None"),
        (24, "PulseMetrics Hospital Dehradun",       "Dehradun",      "Uttarakhand",     "North", "Tier-2", 160, 2021, "None"),
        (25, "PulseMetrics Hospital Ranchi",         "Ranchi",        "Jharkhand",       "East",  "Tier-2", 150, 2022, "None"),
    ]
    cols = ["hospital_id","hospital_name","city","state","region","tier",
            "bed_capacity","established_year","accreditation"]
    return pd.DataFrame(hospitals, columns=cols)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  DIM_PATIENTS  (~60 000 rows) — UNCHANGED
# ─────────────────────────────────────────────────────────────────────────────

def generate_dim_patients(n: int = 60_000) -> pd.DataFrame:
    first_names = [
        # North India
        "Aarav","Aditi","Aakash","Abhay","Abhinav","Abhishek","Aditya","Ajay",
        "Akash","Akshay","Aman","Amit","Ananya","Anjali","Ankit","Ansh",
        "Arjun","Arnav","Arun","Aryan","Ashish","Ayush","Bhavna","Chetan",
        "Deepa","Deepak","Divya","Gaurav","Harsh","Harsha","Himanshu","Ishaan",
        "Jatin","Karan","Kartik","Kavita","Kiran","Manish","Meera","Mohit",
        "Naveen","Neeraj","Nikhil","Pankaj","Pooja","Prakash","Pranav","Priya",
        "Rahul","Rajat","Rajesh","Rakesh","Ravi","Riya","Rohit","Sahil",
        "Sanjay","Sandeep","Shivam","Shreya","Siddharth","Sneha","Suresh",
        "Tarun","Varun","Vikas","Vikram","Vivek","Yash","Yuvraj",

        # Uttar Pradesh / Bihar / Jharkhand
        "Abhishek","Aditya","Ajit","Anand","Anil","Ankit","Ashok","Avinash",
        "Chandan","Dhananjay","Dheeraj","Dilip","Gopal","Kanhaiya","Manoj",
        "Mukesh","Niraj","Nitish","Pankaj","Pawan","Ranjan","Ravi","Ritesh",
        "Roshan","Santosh","Shubham","Sudhir","Sunil","Vijay","Vinay","Vishal",
        "Vikash","Vivek","Aanchal","Anamika","Ankita","Archana","Kajal",
        "Kanchan","Kavita","Khushboo","Komal","Muskan","Nandini","Neha",
        "Pallavi","Payal","Poonam","Priyanka","Rani","Rashmi","Renu",
        "Richa","Shalini","Shikha","Shweta","Simran","Swati",

        # Rajasthan / Haryana
        "Abhimanyu","Ajay","Amit","Anuj","Arvind","Bhupendra","Dinesh","Gajendra",
        "Hardeep","Hemant","Jagdish","Jaswant","Jitendra","Kuldeep","Mahendra",
        "Mahipal","Manoj","Mohan","Naresh","Naveen","Omprakash","Pardeep",
        "Raghav","Rajendra","Ramesh","Ravindra","Sanjay","Satyendra","Surendra",
        "Vijender","Vijay","Anju","Chanchal","Deepika","Geeta","Jyoti","Kiran",
        "Mamta","Meena","Monika","Nisha","Preeti","Rekha","Ritu","Sakshi",
        "Sarita","Seema","Sonam","Sunita",

        # Punjab / Haryana / Himachal
        "Amandeep","Amrit","Armaan","Balraj","Daljit","Dilpreet","Gagandeep",
        "Gurdeep","Gurpreet","Harman","Harjeet","Harmeet","Harpreet","Jasdeep",
        "Jasmeet","Jaspreet","Karan","Maninder","Manjot","Manpreet","Navdeep",
        "Navjot","Parminder","Prabhjot","Rajveer","Ranjit","Simran","Sukhdeep",
        "Sukhwinder","Tejinder","Amandeep","Gurleen","Harleen","Jasleen",
        "Kamalpreet","Kirandeep","Navneet","Rupinder","Simranjeet",

        # Gujarat
        "Aarav","Aayush","Akash","Bhavin","Chirag","Darshan","Dev","Dhruv",
        "Harsh","Hiren","Jignesh","Karan","Kunal","Manan","Meet","Mihir",
        "Nirav","Parth","Rahul","Rishi","Rohan","Tushar","Vatsal","Yash",
        "Yuvraj","Ami","Bhakti","Bhavna","Hetal","Janki","Krupa","Mansi",
        "Nidhi","Nisha","Pinal","Riddhi","Riya","Shivani","Sneha",

        # Maharashtra
        "Aditya","Akash","Amol","Aniket","Atharva","Chetan","Dhananjay","Gaurav",
        "Kunal","Mahesh","Manish","Mayur","Nikhil","Omkar","Pranav","Rahul",
        "Rohit","Sachin","Sagar","Sameer","Sanket","Shantanu","Shreyas",
        "Swapnil","Tejas","Vaibhav","Vishal","Aditi","Ananya","Ashwini",
        "Deepali","Gauri","Kavita","Madhura","Megha","Prachi","Radhika",
        "Rutuja","Sayali","Snehal","Tejal","Vaishnavi",

        # Goa
        "Adrian","Alfred","Alisha","Anita","Anthony","Clara","Daniel","David",
        "Dev","Ethan","Felix","Joel","John","Kevin","Liam","Maria","Maya",
        "Michael","Neil","Noel","Rhea","Ryan","Samuel","Sanjay","Sean",
        "Sophia","Victor","Xavier",

        # Karnataka
        "Aditya","Akshay","Arjun","Chetan","Darshan","Dhanush","Girish","Harish",
        "Karthik","Kiran","Manjunath","Naveen","Prajwal","Prakash","Rahul",
        "Rakesh","Rohan","Sandeep","Santosh","Shashank","Shreyas","Siddharth",
        "Tejas","Vijay","Vishal","Aishwarya","Ananya","Deepa","Divya","Kavya",
        "Lakshmi","Meghana","Pooja","Priya","Rakshitha","Shreya","Sneha",

        # Kerala
        "Abhinav","Adarsh","Ajay","Akhil","Amal","Arjun","Arun","Deepak",
        "Gokul","Hari","Harikrishnan","Jithin","Kiran","Manu","Nikhil",
        "Rahul","Rakesh","Sanjay","Sreehari","Vishnu","Vivek","Ananya",
        "Anjali","Athira","Devika","Diya","Keerthana","Lakshmi","Meera",
        "Parvathy","Remya","Shreya","Sneha","Swetha",

        # Tamil Nadu
        "Aadhavan","Aarav","Adithya","Ajay","Aravind","Ashwin","Bala","Dinesh",
        "Gokul","Hari","Harish","Karthik","Kavin","Lokesh","Manikandan",
        "Mohan","Prakash","Pranav","Raghav","Rahul","Ramesh","Sanjay",
        "Sathish","Surya","Vignesh","Vijay","Vishal","Aishwarya","Ananya",
        "Divya","Harini","Keerthana","Lakshmi","Meena","Nandhini","Priya",
        "Ramya","Shreya","Sneha","Swathi",

        # Andhra Pradesh / Telangana
        "Abhinav","Aditya","Akash","Arjun","Ashwin","Bhargav","Chaitanya",
        "Charan","Harsha","Karthik","Kiran","Krishna","Mahesh","Manish",
        "Naveen","Nikhil","Pavan","Pranav","Rahul","Rakesh","Rohit","Sandeep",
        "Srikanth","Tarun","Vamshi","Vamsi","Varun","Venkatesh","Yashwanth",
        "Akhila","Ananya","Bhavana","Divya","Keerthi","Lavanya","Manasa",
        "Meghana","Pooja","Priyanka","Sahithi","Sravani","Sowmya","Swathi",

        # Odisha
        "Abhijit","Abhishek","Aditya","Ajit","Amit","Anil","Ankit","Arindam",
        "Ashish","Debashish","Debendra","Deepak","Dibakar","Gopal","Manas",
        "Manoj","Niranjan","Pankaj","Prakash","Prasanta","Rahul","Rakesh",
        "Ranjan","Sambit","Sandeep","Sanjay","Satyajit","Shubham","Subham",
        "Sujit","Suman","Ananya","Anu","Archana","Barsha","Debasmita",
        "Ipsita","Jyoti","Madhumita","Mamata","Priyanka","Rashmi","Sasmita",

        # West Bengal
        "Abhijit","Abhishek","Aditya","Anirban","Arindam","Arnab","Avik",
        "Debanjan","Debashis","Dipankar","Indranil","Joy","Koushik","Mainak",
        "Niloy","Partha","Pratik","Rahul","Ritwik","Sagnik","Sambit","Sourav",
        "Subhajit","Ananya","Debolina","Ishita","Madhumita","Moumita","Riya",
        "Rupsa","Shreya","Sneha","Sohini",

        # Assam / Northeast
        "Anupam","Arindam","Bikash","Debajit","Dhruba","Himanta","Jayanta",
        "Kunal","Manash","Niloy","Partha","Ranjit","Rupam","Sanjib","Saurav",
        "Barnali","Bipasha","Dipika","Madhumita","Mousumi","Nandita","Pallavi",
        "Trishna","Bishal","Dipu","Hridoy","Pranjal","Raktim","Rohan",

        # Sikkim / Himalayan Northeast
        "Dawa","Karma","Lobsang","Mingma","Nawang","Pema","Phurba","Rinchen",
        "Sonam","Tashi","Tenpa","Tshering","Yangchen","Dolma","Kelsang","Lhamo",
        "Tenzin","Dorjee","Jigme","Pasang",

        # Arunachal Pradesh
        "Tana","Taba","Lobsang","Nyima","Dawa","Tashi","Dorjee","Pema",
        "Nabam","Maya","Tenzin","Karma","Leki","Tara","Joram","Riba",
        "Toko","Nalo","Bamin","Mopin",

        # Nagaland
        "Aren","Ato","Bendang","Imkong","Kaito","Kene","Kezhalie","Khrienuo",
        "Lanuakum","Mughato","Neibou","Temjen","Toshi","Viku","Zuboni",
        "Arenla","Akum","Chubala","Keneilhou","Mhonika",

        # Meghalaya
        "Benedict","Conrad","Daryl","Denzel","Everett","Frederick","John",
        "Kevin","Lester","Mark","Meban","Ricky","Ronald","Samuel","Sharon",
        "Vincent","Adeline","Angela","Diana","Evelyn","Grace","Janet","Mary",
        "Mercy","Monica","Rose","Samuel",

        # Manipur
        "Bishnupada","Chaoba","Ibocha","Irom","Khuraijam","Laishram",
        "Meghachandra","Ningthoujam","Oinam","Okram","Rajkumar","Sanatomba",
        "Sanjit","Thangjam","Yumnam","Bimala","Chanu","Ibemcha","Memcha",
        "Ranjita","Sharmila",

        # Mizoram
        "Lalbiak","Lalhmingmawia","Lalhruaitluanga","Lalmuanzuali",
        "Lalremruata","Lalrinawma","Malsawma","Rohmingliana",
        "Vanlalhruaia","Zothanmawia","Chawngthu","Hmingthanzuala",
        "Rinawma","Ruatfela"
    ]

    last_names = [
        # Pan-India
        "Sharma","Verma","Gupta","Singh","Kumar","Agarwal","Joshi","Sinha",
        "Mehta","Kapoor","Malhotra","Chopra","Mishra","Tiwari","Pandey",
        "Srivastava","Saxena","Jain","Bansal","Arora","Khanna","Sethi",

        # Uttar Pradesh / Bihar / Jharkhand
        "Yadav","Mishra","Jha","Pandey","Tiwari","Tripathi","Dubey","Shukla",
        "Srivastava","Sinha","Prasad","Choudhary","Thakur","Maurya","Jaiswal",
        "Kushwaha","Rajbhar","Sah","Mahto","Mahato","Soren","Munda","Oraon",
        "Tirkey","Toppo","Lakra","Ekka","Kujur",

        # Rajasthan / Haryana
        "Rajput","Rathore","Shekhawat","Chauhan","Meena","Gurjar","Gujjar",
        "Jat","Bishnoi","Solanki","Sisodia","Tanwar","Kachhwaha","Saini",
        "Dahiya","Dalal","Deswal","Malik","Kadian","Ahlawat","Hooda","Gulia",
        "Rathi","Punia","Sheoran","Rawat",

        # Gujarat
        "Patel","Shah","Desai","Mehta","Joshi","Modi","Trivedi","Dave","Bhatt",
        "Parikh","Thakkar","Panchal","Solanki","Chauhan","Vyas","Gandhi",
        "Raval","Pandya","Gohil","Mistry","Parekh",

        # Maharashtra
        "Patil","Deshmukh","Kulkarni","Jadhav","Pawar","Shinde","Chavan",
        "Gaikwad","More","Bhosale","Joshi","Deshpande","Kadam","Sawant",
        "Thakur","Salunkhe","Gore","Mane","Mhatre","Kale","Dighe","Wagh",

        # Goa
        "D'Souza","Fernandes","Pereira","Rodrigues","Gomes","Dias","Costa",
        "Almeida","Carvalho","De Souza","Naik","Kamat","Rane","Desai","Shetye",

        # Karnataka
        "Shetty","Gowda","Rao","Hegde","Bhat","Pai","Naik","Kulkarni","Patil",
        "Deshpande","Joshi","Acharya","Sharma","Reddy","Kamath","Adiga",
        "Murthy","Nayak","Urs","Prabhu","Karkera","Poojary",

        # Kerala
        "Nair","Menon","Pillai","Panicker","Kurup","Varma","Namboothiri",
        "Krishnan","Warrier","Iyer","Thomas","Joseph","Mathew","George",
        "Kurian","Jacob","Abraham","Chacko","Nambiar","Madhavan",

        # Tamil Nadu
        "Iyer","Iyengar","Pillai","Nadar","Gounder","Thevar","Chettiar",
        "Mudaliar","Naidu","Reddy","Rao","Krishnan","Subramanian","Murugan",
        "Shanmugam","Rajendran","Balakrishnan","Srinivasan","Raman","Ilangovan",

        # Andhra Pradesh / Telangana
        "Reddy","Naidu","Chowdary","Rao","Varma","Prasad","Krishna","Konduri",
        "Gadde","Gollapudi","Kommineni","Kandula","Penumala","Yarlagadda",
        "Goud","Yadav","Gaddam","Peddireddy","Nallamothu","Mallepally",

        # Odisha
        "Das","Mohanty","Mishra","Patnaik","Nayak","Behera","Jena","Sahoo",
        "Pradhan","Rout","Barik","Samal","Acharya","Panda","Dhal","Maharana",
        "Swain","Mahapatra","Tripathy","Dash","Sahu","Parida","Behera",

        # West Bengal
        "Banerjee","Chatterjee","Mukherjee","Ganguly","Das","Dutta","Ghosh",
        "Bose","Sengupta","Roy","Sen","Sarkar","Bhattacharya","Basu","Chakraborty",
        "Mitra","Saha","Majumdar","De","Pal","Biswas","Mondal",

        # Assam
        "Borah","Saikia","Gogoi","Dutta","Das","Barua","Hazarika","Bhuyan",
        "Kalita","Sarma","Borthakur","Phukan","Goswami","Choudhury","Deka",
        "Mahanta",

        # Punjab
        "Sandhu","Gill","Sidhu","Brar","Dhillon","Mann","Bajwa","Grewal",
        "Randhawa","Cheema","Sohal","Aulakh","Bedi","Kapoor","Chawla","Arora",
        "Khanna","Sethi","Bhullar","Toor",

        # Himachal / Uttarakhand
        "Thakur","Sharma","Verma","Chauhan","Rana","Katoch","Chandel","Pathania",
        "Sood","Negi","Kanwar","Jaswal","Bhardwaj","Rawat","Bisht","Bhandari",
        "Kandari","Pundir","Dhyani","Semwal","Gusain","Nautiyal",

        # Sikkim
        "Bhutia","Lepcha","Tamang","Sherpa","Subba","Rai","Gurung","Chettri",
        "Pradhan","Limboo",

        # Nagaland / Northeast
        "Ao","Angami","Sumi","Lotha","Konyak","Sangtam","Rongmei","Phom",
        "Chang","Khiamniungan","Rengma","Yimchunger",

        # Meghalaya
        "Lyngdoh","Khongwir","Nongkynrih","Syiem","Mawlong","Marak","Sangma",
        "Momin","Rymbai","Kharshiing","Warjri",

        # Mizoram
        "Ralte","Hmar","Pachuau","Sailo","Chawngthu","Fanai","Zote","Vanlalruata",

        # Manipur
        "Meitei","Laishram","Oinam","Yumnam","Ningthoujam","Thangjam","Okram",
        "Khuraijam","Rajkumar","Chakma",

        # Tripura
        "Debbarma","Reang","Jamatia","Tripura","Chakma","Das","Dutta","Saha",
        "Roy","Bhowmik","Paul","Choudhury"
    ]

    cities_states = [
        ("Mumbai","Maharashtra"),("Delhi","Delhi"),("Bengaluru","Karnataka"),
        ("Hyderabad","Telangana"),("Chennai","Tamil Nadu"),("Kolkata","West Bengal"),
        ("Pune","Maharashtra"),("Ahmedabad","Gujarat"),("Jaipur","Rajasthan"),
        ("Lucknow","Uttar Pradesh"),("Bhubaneswar","Odisha"),("Kochi","Kerala"),
        ("Chandigarh","Punjab"),("Indore","Madhya Pradesh"),("Nagpur","Maharashtra"),
        ("Coimbatore","Tamil Nadu"),("Visakhapatnam","Andhra Pradesh"),("Patna","Bihar"),
        ("Guwahati","Assam"),("Surat","Gujarat"),("Ranchi","Jharkhand"),
        ("Bhopal","Madhya Pradesh"),("Dehradun","Uttarakhand"),("Vadodara","Gujarat"),
    ]

    blood_groups     = ["A+","A-","B+","B-","AB+","AB-","O+","O-"]
    patient_types    = ["New","New","New","Repeat","Repeat"]           # 60% new
    referral_sources = ["Walk-in","Walk-in","Doctor Referral","Insurance","Corporate","Online"]
    insurance_types  = ["Self-Pay","Cashless","Reimbursement","Corporate TPA","Government"]
    insurance_weights= [0.30, 0.28, 0.15, 0.17, 0.10]

    # ── v3: Realistic bimodal age distribution (Indian hospital demographics) ──
    age_bands   = [(0, 5), (6, 12), (13, 18), (19, 30), (31, 45), (46, 60), (61, 75), (76, 90)]
    age_weights = [0.08,    0.05,    0.04,     0.12,     0.22,     0.25,     0.16,     0.08]
    ages = []
    for _ in range(n):
        band = random.choices(age_bands, weights=age_weights, k=1)[0]
        ages.append(random.randint(band[0], band[1]))

    ids      = [f"P-{str(i).zfill(6)}" for i in range(1, n + 1)]
    names_f  = [random.choice(first_names) for _ in range(n)]
    names_l  = [random.choice(last_names)  for _ in range(n)]
    genders  = random.choices(["Male","Female","Other"], weights=[50,48,2], k=n)
    blood    = random.choices(blood_groups, k=n)
    cs_pairs = [random.choice(cities_states) for _ in range(n)]
    cities   = [c for c,_ in cs_pairs]
    states   = [s for _,s in cs_pairs]
    p_types  = random.choices(patient_types, k=n)
    ins_type = random.choices(insurance_types, weights=insurance_weights, k=n)

    # ── v3: Referral source correlated with insurance type ───────────────
    referral_by_insurance = {
        "Self-Pay":        ["Walk-in","Walk-in","Walk-in","Doctor Referral","Online"],
        "Cashless":        ["Insurance","Insurance","Doctor Referral","Walk-in","Online"],
        "Reimbursement":   ["Doctor Referral","Walk-in","Insurance","Online","Walk-in"],
        "Corporate TPA":   ["Corporate","Corporate","Corporate","Doctor Referral","Walk-in"],
        "Government":      ["Walk-in","Walk-in","Doctor Referral","Walk-in","Insurance"],
    }
    ref_src = [random.choice(referral_by_insurance.get(it, referral_sources)) for it in ins_type]
    reg_dates= [random_date(datetime(2023,1,1), datetime(2024,12,31)).date() for _ in range(n)]

    df = pd.DataFrame({
        "patient_id"          : ids,
        "patient_name"        : [f"{f} {l}" for f,l in zip(names_f, names_l)],
        "age"                 : ages,
        "gender"              : genders,
        "blood_group"         : blood,
        "city_of_residence"   : cities,
        "state_of_residence"  : states,
        "patient_type"        : p_types,
        "referral_source"     : ref_src,
        "insurance_type"      : ins_type,
        "registration_date"   : reg_dates,
    })

    # ── Dirty data: age anomalies ──────────────────────────────────────────
    noise_idx = random.sample(range(n), int(n * 0.008))   # 0.8%
    for i in noise_idx:
        df.at[i, "age"] = random.choice([0, 0, 115, 130, -1])

    # ── Dirty data: duplicate patients (slightly different names) ──────────
    dup_idx = random.sample(range(n), int(n * 0.005))     # 0.5%
    dups = df.iloc[dup_idx].copy()
    dups["patient_id"] = [f"P-{str(i + n).zfill(6)}" for i in range(len(dups))]
    dups["patient_name"] = dups["patient_name"].apply(
        lambda x: x.replace("a","@",1) if "a" in x else x + " Jr"
    )
    df = pd.concat([df, dups], ignore_index=True)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# 3.  DIM_DOCTORS  (~800 rows) — UNCHANGED
# ─────────────────────────────────────────────────────────────────────────────

def generate_dim_doctors(hospitals_df: pd.DataFrame, n: int = 800) -> pd.DataFrame:
    specializations = {
        "Cardiology"       : "MD",
        "Orthopedics"      : "MS",
        "Oncology"         : "DM",
        "Neurology"        : "DM",
        "Gastroenterology" : "DM",
        "Pulmonology"      : "MD",
        "Nephrology"       : "DM",
        "Endocrinology"    : "DM",
        "Gynecology"       : "MS",
        "Pediatrics"       : "MD",
        "General Surgery"  : "MS",
        "Dermatology"      : "MD",
        "Psychiatry"       : "MD",
        "Ophthalmology"    : "MS",
        "ENT"              : "MS",
        "Emergency Medicine": "MBBS",
        "Radiology"        : "MD",
        "Anesthesiology"   : "MD",
        "Urology"          : "MS",
        "Rheumatology"     : "DM",
    }
    dept_map = {
        "Cardiology":"Cardiac Sciences","Orthopedics":"Bone & Joint",
        "Oncology":"Cancer Care","Neurology":"Neurosciences",
        "Gastroenterology":"Digestive Health","Pulmonology":"Respiratory",
        "Nephrology":"Renal Sciences","Endocrinology":"Diabetes & Endocrine",
        "Gynecology":"Women & Child","Pediatrics":"Women & Child",
        "General Surgery":"Surgery","Dermatology":"Skin & Hair",
        "Psychiatry":"Mental Health","Ophthalmology":"Eye Care",
        "ENT":"ENT","Emergency Medicine":"Emergency & Trauma",
        "Radiology":"Diagnostics","Anesthesiology":"Critical Care",
        "Urology":"Urology","Rheumatology":"Rheumatology",
    }
    first = ["Dr. Anil","Dr. Sunita","Dr. Ramesh","Dr. Priya","Dr. Vijay",
             "Dr. Meena","Dr. Suresh","Dr. Kavitha","Dr. Rajiv","Dr. Deepa",
             "Dr. Harish","Dr. Lakshmi","Dr. Girish","Dr. Ananya","Dr. Mohan",
             "Dr. Divya","Dr. Srinivas","Dr. Rekha","Dr. Arjun","Dr. Nandita"]
    last  = ["Sharma","Reddy","Nair","Gupta","Iyer","Patel","Kumar","Mehta",
             "Joshi","Rao","Pillai","Das","Bose","Mishra","Tiwari","Agarwal"]
    emp_types = ["Full-time","Full-time","Full-time","Visiting","Consultant"]

    hospital_ids   = hospitals_df["hospital_id"].tolist()
    spec_list      = list(specializations.keys())
    rows = []
    for i in range(1, n + 1):
        sp   = random.choice(spec_list)
        qual = specializations[sp]
        rows.append({
            "doctor_id"         : f"D-{str(i).zfill(4)}",
            "doctor_name"       : f"{random.choice(first)} {random.choice(last)}",
            "specialization"    : sp,
            "department"        : dept_map[sp],
            "hospital_id"       : random.choice(hospital_ids),
            "qualification"     : qual,
            "experience_years"  : random.randint(2, 35),
            "consultation_fee"  : random.choice([500,700,800,1000,1200,1500,2000]),
            "employment_type"   : random.choice(emp_types),
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# 4.  DIM_ICD_CODES  (~57 rows) — UNCHANGED
# ─────────────────────────────────────────────────────────────────────────────

def generate_dim_icd_codes() -> pd.DataFrame:
    raw = [
        # Cardiovascular
        ("I21.0","Acute Myocardial Infarction","Cardiovascular","Critical",True),
        ("I10",  "Essential Hypertension",      "Cardiovascular","Moderate",True),
        ("I50.0","Congestive Heart Failure",    "Cardiovascular","Severe",  True),
        ("I48",  "Atrial Fibrillation",         "Cardiovascular","Moderate",True),
        ("I25",  "Chronic Ischaemic Heart Disease","Cardiovascular","Severe",True),
        ("I63",  "Cerebral Infarction",         "Cardiovascular","Critical",False),
        ("I64",  "Stroke NOS",                  "Cardiovascular","Critical",False),
        # Respiratory
        ("J18.9","Pneumonia Unspecified",        "Respiratory","Severe", False),
        ("J44",  "COPD",                         "Respiratory","Severe", True),
        ("J45",  "Asthma",                       "Respiratory","Moderate",True),
        ("J12",  "Viral Pneumonia",              "Respiratory","Severe", False),
        ("J96",  "Respiratory Failure",          "Respiratory","Critical",False),
        # Endocrine
        ("E11",  "Type 2 Diabetes Mellitus",     "Endocrine","Moderate",True),
        ("E10",  "Type 1 Diabetes Mellitus",     "Endocrine","Moderate",True),
        ("E78",  "Hyperlipidaemia",              "Endocrine","Minor",   True),
        ("E03",  "Hypothyroidism",               "Endocrine","Minor",   True),
        ("E05",  "Hyperthyroidism",              "Endocrine","Moderate",True),
        # Gastroenterology
        ("K74",  "Liver Cirrhosis",              "Gastroenterology","Severe",True),
        ("K92.1","Melaena",                      "Gastroenterology","Severe",False),
        ("K57",  "Diverticular Disease",         "Gastroenterology","Moderate",True),
        ("K29",  "Gastritis",                    "Gastroenterology","Minor",False),
        ("K80",  "Cholelithiasis",               "Gastroenterology","Moderate",False),
        ("K85",  "Acute Pancreatitis",           "Gastroenterology","Critical",False),
        # Renal
        ("N18",  "Chronic Kidney Disease",       "Renal","Severe",True),
        ("N17",  "Acute Kidney Injury",          "Renal","Critical",False),
        ("N39.0","Urinary Tract Infection",      "Renal","Minor",False),
        # Neurology
        ("G20",  "Parkinson Disease",            "Neurology","Severe",True),
        ("G35",  "Multiple Sclerosis",           "Neurology","Severe",True),
        ("G43",  "Migraine",                     "Neurology","Minor",True),
        ("G40",  "Epilepsy",                     "Neurology","Moderate",True),
        ("G91",  "Hydrocephalus",                "Neurology","Severe",False),
        # Oncology
        ("C34",  "Lung Cancer",                  "Oncology","Critical",False),
        ("C50",  "Breast Cancer",                "Oncology","Severe",False),
        ("C18",  "Colon Cancer",                 "Oncology","Severe",False),
        ("C61",  "Prostate Cancer",              "Oncology","Severe",False),
        ("C92",  "Myeloid Leukaemia",            "Oncology","Critical",False),
        # Orthopedics
        ("M16",  "Hip Osteoarthritis",           "Orthopedics","Moderate",True),
        ("M17",  "Knee Osteoarthritis",          "Orthopedics","Moderate",True),
        ("S72",  "Fracture of Femur",            "Orthopedics","Severe",False),
        ("M54",  "Back Pain",                    "Orthopedics","Minor",False),
        ("M80",  "Osteoporosis with Fracture",   "Orthopedics","Moderate",True),
        # Gynecology
        ("O80",  "Normal Delivery",              "Gynecology","Minor",False),
        ("O82",  "Caesarean Section",            "Gynecology","Moderate",False),
        ("N91",  "Amenorrhoea",                  "Gynecology","Minor",False),
        ("D25",  "Uterine Fibroids",             "Gynecology","Moderate",False),
        # Pediatrics
        ("A09",  "Gastroenteritis (Paediatric)", "Pediatrics","Minor",False),
        ("J06",  "Acute URTI (Paediatric)",      "Pediatrics","Minor",False),
        ("P07",  "Preterm Newborn",              "Pediatrics","Critical",False),
        # Infectious
        ("A41",  "Sepsis",                       "Infectious","Critical",False),
        ("B34",  "Viral Infection NOS",          "Infectious","Minor",False),
        ("A90",  "Dengue Fever",                 "Infectious","Moderate",False),
        ("A01",  "Typhoid Fever",                "Infectious","Moderate",False),
        ("B50",  "Malaria",                      "Infectious","Moderate",False),
        # Psychiatry
        ("F32",  "Depressive Episode",           "Psychiatry","Moderate",True),
        ("F20",  "Schizophrenia",                "Psychiatry","Severe",True),
        ("F10",  "Alcohol Use Disorder",         "Psychiatry","Moderate",True),
        ("F41",  "Anxiety Disorder",             "Psychiatry","Minor",True),
    ]
    cols = ["icd_code","diagnosis_name","category","severity_level","is_chronic"]
    return pd.DataFrame(raw, columns=cols)


# ─────────────────────────────────────────────────────────────────────────────
# 5.  FACT_ADMISSIONS  (~120 000 rows) — v2: Non-uniform distribution
# ─────────────────────────────────────────────────────────────────────────────

def generate_fact_admissions(patients_df, doctors_df, hospitals_df, icd_df,
                              n: int = 120_000) -> pd.DataFrame:
    patient_ids  = patients_df["patient_id"].tolist()
    doctor_ids   = doctors_df["doctor_id"].tolist()

    # ── v2: Hospital selection weighted by bed capacity ────────────────────
    hospital_ids     = hospitals_df["hospital_id"].tolist()
    hospital_weights = hospitals_df["bed_capacity"].tolist()

    # ── v2: Build doctor lookup by hospital for doctor-hospital matching ──
    doc_by_hosp = doctors_df.groupby("hospital_id")["doctor_id"].apply(list).to_dict()

    # ── v2: Hospital tier lookup (for metro-specific admission type mix) ──
    hosp_tier = hospitals_df.set_index("hospital_id")["tier"].to_dict()

    # ── v2: ICD lookup tables ──────────────────────────────────────────────
    icd_codes = icd_df["icd_code"].tolist()
    icd_cats  = icd_df["category"].tolist()
    icd_sevs  = icd_df["severity_level"].tolist()
    icd_lookup = {}
    for code, cat, sev in zip(icd_codes, icd_cats, icd_sevs):
        icd_lookup[code] = (cat, sev)

    # ── v2: ICD category → Department mapping ─────────────────────────────
    cat_to_dept = {
        "Cardiovascular":    "Cardiac Sciences",
        "Respiratory":       "Respiratory",
        "Endocrine":         "Diabetes & Endocrine",
        "Gastroenterology":  "Digestive Health",
        "Renal":             "Renal Sciences",
        "Neurology":         "Neurosciences",
        "Oncology":          "Cancer Care",
        "Orthopedics":       "Bone & Joint",
        "Gynecology":        "Women & Child",
        "Pediatrics":        "Women & Child",
        "Infectious":        "Emergency & Trauma",
        "Psychiatry":        "Neurosciences",
    }

    # ── v2: Seasonal weights for ICD categories (Indian climate) ──────────
    unique_cats = list(set(icd_cats))
    seasonal_cat_weights = {}
    for m in range(1, 13):
        w = {cat: 1.0 for cat in unique_cats}
        if m in [6, 7, 8, 9]:      # Monsoon
            w["Infectious"]     = 2.5
            w["Respiratory"]    = 1.8
            w["Pediatrics"]     = 1.4   # Paediatric GI/respiratory in monsoon
        if m in [12, 1, 2]:         # Winter
            w["Cardiovascular"] = 1.8
            w["Respiratory"]    = 1.5
            w["Orthopedics"]    = 1.2   # Falls in cold/fog
        if m in [3, 4, 5]:          # Summer
            w["Gastroenterology"] = 1.5
            w["Renal"]            = 1.3  # Dehydration → AKI/UTI
            w["Infectious"]       = 1.2  # Heat-related infections
        if m in [10, 11]:           # Post-monsoon
            w["Endocrine"]      = 1.2   # Post-festive diabetic spikes
        seasonal_cat_weights[m] = w

    # ── v2: Hospital Clinical Profiles (Acuity, ALOS, Readmission, Mortality) ────
    # Drives realistic variation across tertiary flagships vs secondary branches
    hospital_clinical_profiles = {
        # Tier-1 Flagship & Quaternary Referral Centers
        1 : (1.25, 0.058, 0.115),  # Bengaluru (NABH, 650 beds) - ALOS ~6.6d, Readmit 5.8%, Mort 11.5%
        2 : (1.35, 0.052, 0.125),  # Mumbai (JCI, 800 beds)    - ALOS ~7.2d, Readmit 5.2%, Mort 12.5%
        3 : (1.20, 0.062, 0.110),  # Delhi (NABH, 720 beds)     - ALOS ~6.4d, Readmit 6.2%, Mort 11.0%
        4 : (1.15, 0.055, 0.095),  # Chennai (NABH, 600 beds)   - ALOS ~6.1d, Readmit 5.5%, Mort 9.5%
        5 : (1.05, 0.068, 0.090),  # Hyderabad (NABH, 580 beds) - ALOS ~5.6d, Readmit 6.8%, Mort 9.0%
        6 : (1.00, 0.072, 0.085),  # Pune (NABH, 450 beds)      - ALOS ~5.3d, Readmit 7.2%, Mort 8.5%
        7 : (1.10, 0.075, 0.105),  # Kolkata (NABH, 500 beds)   - ALOS ~5.8d, Readmit 7.5%, Mort 10.5%
        8 : (0.95, 0.082, 0.080),  # Ahmedabad (420 beds)       - ALOS ~5.0d, Readmit 8.2%, Mort 8.0%
        # Tier-2 Established & Regional Hubs
        9 : (0.85, 0.088, 0.075),  # Jaipur (320 beds)          - ALOS ~4.5d, Readmit 8.8%, Mort 7.5%
        10: (0.90, 0.112, 0.085),  # Lucknow (300 beds)         - ALOS ~4.8d, Readmit 11.2%, Mort 8.5%
        11: (0.88, 0.078, 0.070),  # Bhubaneswar (NABH, 280)    - ALOS ~4.6d, Readmit 7.8%, Mort 7.0%
        12: (0.82, 0.095, 0.065),  # Chandigarh (260 beds)      - ALOS ~4.3d, Readmit 9.5%, Mort 6.5%
        13: (0.92, 0.056, 0.060),  # Kochi (NABH, 310 beds)     - ALOS ~4.9d, Readmit 5.6%, Mort 6.0%
        # Tier-2 Secondary & Emerging Branches (High Turnover / Routine Care)
        14: (0.75, 0.118, 0.060),  # Indore (240 beds)          - ALOS ~3.9d, Readmit 11.8%, Mort 6.0%
        15: (0.72, 0.115, 0.058),  # Nagpur (220 beds)          - ALOS ~3.8d, Readmit 11.5%, Mort 5.8%
        16: (0.78, 0.068, 0.055),  # Coimbatore (200 beds)      - ALOS ~4.1d, Readmit 6.8%, Mort 5.5%
        17: (0.76, 0.092, 0.055),  # Visakhapatnam (230 beds)   - ALOS ~4.0d, Readmit 9.2%, Mort 5.5%
        18: (0.80, 0.135, 0.085),  # Patna (190 beds)           - ALOS ~4.2d, Readmit 13.5%, Mort 8.5%
        19: (0.70, 0.128, 0.050),  # Guwahati (180 beds)        - ALOS ~3.7d, Readmit 12.8%, Mort 5.0%
        20: (0.75, 0.072, 0.048),  # Thiruvananthapuram (210)   - ALOS ~3.9d, Readmit 7.2%, Mort 4.8%
        21: (0.68, 0.098, 0.045),  # Surat (200 beds)           - ALOS ~3.6d, Readmit 9.8%, Mort 4.5%
        22: (0.67, 0.102, 0.045),  # Vadodara (185 beds)        - ALOS ~3.5d, Readmit 10.2%, Mort 4.5%
        23: (0.69, 0.125, 0.052),  # Bhopal (175 beds)          - ALOS ~3.6d, Readmit 12.5%, Mort 5.2%
        24: (0.64, 0.108, 0.040),  # Dehradun (160 beds)        - ALOS ~3.4d, Readmit 10.8%, Mort 4.0%
        25: (0.62, 0.138, 0.038),  # Ranchi (150 beds)          - ALOS ~3.2d, Readmit 13.8%, Mort 3.8%
    }

    # ── v2: Department-specific LOS (min, mode, max for triangular dist) ──
    dept_los_params = {
        "Cardiac Sciences":      (3, 7, 18),
        "Cancer Care":           (5, 10, 25),
        "Neurosciences":         (3, 7, 18),
        "Critical Care":         (2, 5, 20),
        "Renal Sciences":        (2, 5, 14),
        "Respiratory":           (2, 5, 12),
        "Digestive Health":      (2, 4, 12),
        "Diabetes & Endocrine":  (2, 4, 10),
        "Women & Child":         (1, 3, 8),
        "Bone & Joint":          (3, 6, 14),
        "Surgery":               (2, 5, 14),
        "Emergency & Trauma":    (1, 3, 10),
        "ENT":                   (1, 2, 5),
        "Eye Care":              (1, 1, 3),
        "Diagnostics":           (1, 2, 4),
    }

    # ── v2: Severity multipliers for LOS ──────────────────────────────────
    severity_los_mult = {
        "Critical": 1.5,
        "Severe":   1.2,
        "Moderate": 1.0,
        "Minor":    0.7,
    }

    # ── v2: Severity-linked outcome baseline probabilities ────────────────
    severity_outcomes = {
        "Critical": {"expired": 0.22, "lama": 0.05, "referred": 0.08, "recovered": 0.65, "readmission": 0.14},
        "Severe":   {"expired": 0.10, "lama": 0.07, "referred": 0.07, "recovered": 0.76, "readmission": 0.10},
        "Moderate": {"expired": 0.03, "lama": 0.05, "referred": 0.05, "recovered": 0.87, "readmission": 0.06},
        "Minor":    {"expired": 0.005,"lama": 0.03, "referred": 0.03, "recovered": 0.935,"readmission": 0.03},
    }

    # ── v2: Severity-linked ward type weights ─────────────────────────────
    severity_ward_weights = {
        "Critical": [0.10, 0.05, 0.15, 0.70],   # 70% ICU
        "Severe":   [0.20, 0.20, 0.30, 0.30],   # 30% ICU
        "Moderate": [0.40, 0.30, 0.25, 0.05],   # Standard wards
        "Minor":    [0.55, 0.25, 0.18, 0.02],   # Mostly general
    }

    admission_types  = ["Emergency","Elective","Day-care"]
    ward_types       = ["General","Semi-Private","Private","ICU"]

    # ── v3.1: Widen Monthly admission volume weights (Indian hospital seasonality) ─
    month_volume_weights = {
        1: 1.30,   # Winter cardiac + post-holiday elective surge (~13,000)
        2: 0.82,   # Short month, lower volume (~8,200)
        3: 1.28,   # FY-end insurance utilization rush (~12,800)
        4: 0.65,   # Post-FY lull, slowest elective month (~6,500)
        5: 0.70,   # Peak summer vacation lull (~7,000)
        6: 0.62,   # Pre-monsoon lull trough (~6,200)
        7: 1.40,   # Monsoon vector-borne & infectious outbreak surge (~14,000)
        8: 1.32,   # Continued monsoon infections (~13,200)
        9: 0.88,   # Monsoon receding (~8,800)
        10: 1.10,  # Post-monsoon festive season / elective catch-up (~11,000)
        11: 1.18,  # Pre-winter surge & elective scheduling (~11,800)
        12: 1.45,  # Winter peak + year-end corporate insurance exhaustion (~14,500)
    }

    # ── v3.1: Seasonal Acuity Multiplier for Length of Stay ────────────────
    # Winter cases (cardiac, stroke, chronic COPD) require longer recovery (7-8 days)
    # Monsoon cases (dengue, malaria, acute gastroenteritis) have fast turnover (3-5 days)
    month_los_mult = {
        1: 1.28, 2: 1.22, 3: 1.05, 4: 0.95, 5: 0.88, 6: 0.78,
        7: 0.70, 8: 0.74, 9: 0.82, 10: 1.00, 11: 1.12, 12: 1.30,
    }

    # ── v3: Weekday vs Weekend weights ─────────────────────────────────────
    dow_weights = {0: 1.15, 1: 1.12, 2: 1.10, 3: 1.08, 4: 1.05, 5: 0.78, 6: 0.72}

    # ── v3: Pre-allocate admissions across months based on volume weights ──
    import calendar
    month_list = list(range(1, 13))
    month_w = [month_volume_weights[m] for m in month_list]
    total_w = sum(month_w)
    month_quotas = {m: max(1, int(round(n * month_volume_weights[m] / total_w)))
                    for m in month_list}
    # Adjust to exactly n
    diff = n - sum(month_quotas.values())
    if diff > 0:
        for m in [12, 1, 3]:  # add to peak months
            month_quotas[m] += diff // 3
        month_quotas[12] += diff - (diff // 3) * 3
    elif diff < 0:
        for m in [6, 4, 5]:   # remove from low months
            month_quotas[m] += diff // 3
        month_quotas[6] += diff - (diff // 3) * 3

    # ── v3: Pre-generate all admission dates with weekday bias ─────────────
    all_adm_dates = []
    for m in month_list:
        year = 2024
        days_in_month = calendar.monthrange(year, m)[1]
        # Build day-of-week weights for each day in this month
        day_list = list(range(1, days_in_month + 1))
        day_wts = [dow_weights[datetime(year, m, d).weekday()] for d in day_list]
        chosen_days = random.choices(day_list, weights=day_wts, k=month_quotas[m])
        for d in chosen_days:
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            all_adm_dates.append(datetime(year, m, d, hour, minute))
    random.shuffle(all_adm_dates)

    # ── v3: Hospital department specialization profiles ────────────────────
    # Each hospital has a "center of excellence" that gets extra case share
    # Format: {hospital_id: {dept: weight_multiplier}} — multiplied on top of ICD-based dept
    default_dept_weights = {
        "Cardiac Sciences": 1.0, "Cancer Care": 1.0, "Neurosciences": 1.0,
        "Critical Care": 1.0, "Renal Sciences": 1.0, "Respiratory": 1.0,
        "Digestive Health": 1.0, "Diabetes & Endocrine": 1.0, "Women & Child": 1.0,
        "Bone & Joint": 1.0, "Surgery": 1.0, "Emergency & Trauma": 1.0,
        "ENT": 1.0, "Eye Care": 1.0, "Diagnostics": 1.0, "Mental Health": 1.0,
    }
    hospital_dept_specialty = {
        # Tier-1: Each flagship has 2-3 specializations as CoE
        1:  {"Cancer Care": 2.0, "Neurosciences": 1.8, "Cardiac Sciences": 1.5},           # Bengaluru
        2:  {"Cardiac Sciences": 2.5, "Cancer Care": 1.8, "Renal Sciences": 1.5},           # Mumbai
        3:  {"Bone & Joint": 2.0, "Emergency & Trauma": 1.8, "Neurosciences": 1.5},         # Delhi
        4:  {"Cardiac Sciences": 1.8, "Cancer Care": 2.0, "Digestive Health": 1.5},          # Chennai
        5:  {"Cancer Care": 1.8, "Cardiac Sciences": 1.5, "Respiratory": 1.5},               # Hyderabad
        6:  {"Bone & Joint": 2.0, "Women & Child": 1.8, "Surgery": 1.5},                     # Pune
        7:  {"Neurosciences": 2.0, "Cardiac Sciences": 1.5, "Digestive Health": 1.5},         # Kolkata
        8:  {"Cardiac Sciences": 1.5, "Digestive Health": 1.8, "Eye Care": 1.5},              # Ahmedabad
        # Tier-2: Each has 1-2 specializations
        9:  {"Bone & Joint": 1.8, "Women & Child": 1.5},                                      # Jaipur
        10: {"Women & Child": 2.0, "Respiratory": 1.5},                                       # Lucknow
        11: {"Cancer Care": 1.8, "Digestive Health": 1.5},                                     # Bhubaneswar
        12: {"Bone & Joint": 1.8, "ENT": 1.5},                                                # Chandigarh
        13: {"Neurosciences": 2.0, "Cardiac Sciences": 1.8},                                  # Kochi
        14: {"Women & Child": 1.8, "Surgery": 1.5},                                           # Indore
        15: {"Respiratory": 1.8, "Surgery": 1.5},                                             # Nagpur
        16: {"Cardiac Sciences": 1.8, "Diabetes & Endocrine": 1.5},                           # Coimbatore
        17: {"Cancer Care": 1.5, "Respiratory": 1.5},                                         # Visakhapatnam
        18: {"Women & Child": 1.8, "Emergency & Trauma": 1.5},                                # Patna
        19: {"Respiratory": 1.8, "Emergency & Trauma": 1.5},                                  # Guwahati
        20: {"Neurosciences": 1.5, "Cardiac Sciences": 1.5},                                  # Thiruvananthapuram
        21: {"Digestive Health": 1.8, "Diabetes & Endocrine": 1.5},                            # Surat
        22: {"Eye Care": 1.8, "ENT": 1.5},                                                    # Vadodara
        23: {"Respiratory": 1.5, "Women & Child": 1.5},                                       # Bhopal
        24: {"Bone & Joint": 1.8, "Respiratory": 1.5},                                        # Dehradun
        25: {"Emergency & Trauma": 1.8, "Surgery": 1.5},                                      # Ranchi
    }

    # ── v3: Gender-biased patient selection by department ──────────────────
    patient_genders = patients_df.set_index("patient_id")["gender"].to_dict()
    male_patients   = [pid for pid, g in patient_genders.items() if g == "Male"]
    female_patients = [pid for pid, g in patient_genders.items() if g == "Female"]
    other_patients  = [pid for pid, g in patient_genders.items() if g == "Other"]

    dept_gender_weights = {
        "Women & Child":         [0.05, 0.93, 0.02],   # 93% Female
        "Bone & Joint":          [0.60, 0.38, 0.02],   # 60% Male
        "Cardiac Sciences":      [0.65, 0.33, 0.02],   # 65% Male
        "Cancer Care":           [0.48, 0.50, 0.02],   # Balanced
        "Surgery":               [0.58, 0.40, 0.02],   # Slightly male
        "Emergency & Trauma":    [0.62, 0.36, 0.02],   # Male-heavy trauma
    }
    default_gender_wt = [0.50, 0.48, 0.02]
    gender_pools = [male_patients, female_patients, other_patients]

    rows = []
    for i in range(1, n + 1):
        # 1. v3: Admission date from pre-allocated seasonal + weekday-weighted dates
        adm_date   = all_adm_dates[i - 1]
        month      = adm_date.month
        quarter    = f"Q{(month - 1)//3 + 1}"

        # 2. v2: ICD code with seasonal weighting
        month_weights = seasonal_cat_weights[month]
        icd_weights   = [month_weights.get(cat, 1.0) for cat in icd_cats]
        icd_code      = random.choices(icd_codes, weights=icd_weights, k=1)[0]
        cat, severity = icd_lookup[icd_code]

        # 3. v3: Department from ICD category + hospital specialization bias
        base_dept = cat_to_dept.get(cat, "Surgery")
        roll = random.random()
        if roll < 0.80:
            dept = base_dept
        elif roll < 0.90:
            dept = "Surgery"
        elif roll < 0.95:
            dept = random.choice(["ENT", "Eye Care"])
        else:
            dept = "Diagnostics"

        # 4. v2: Hospital selection & tier properties
        hospital_id = random.choices(hospital_ids, weights=hospital_weights, k=1)[0]

        # v3: Apply hospital specialization — if dept matches a CoE, boost retention;
        # otherwise, randomly reassign to a CoE dept with some probability
        hosp_spec = hospital_dept_specialty.get(hospital_id, {})
        if dept in hosp_spec:
            pass  # Keep — this hospital specializes in this dept
        elif hosp_spec and random.random() < 0.25:
            # 25% chance: redirect to one of this hospital's CoE departments
            coe_depts = list(hosp_spec.keys())
            coe_wts   = [hosp_spec[d] for d in coe_depts]
            dept = random.choices(coe_depts, weights=coe_wts, k=1)[0]

        is_metro = hosp_tier.get(hospital_id) == "Tier-1"
        adm_type = random.choices(
            admission_types,
            weights=[0.40, 0.45, 0.15] if is_metro else [0.25, 0.55, 0.20]
        )[0]

        # v2: Emergency admissions have 40% chance of going to Emergency & Trauma
        if adm_type == "Emergency" and random.random() < 0.40:
            dept = "Emergency & Trauma"
        # v2: Critical severity has 30% chance of going to Critical Care
        if severity == "Critical" and random.random() < 0.30:
            dept = "Critical Care"

        # 5. v2: Doctor from same hospital where possible
        if hospital_id in doc_by_hosp and doc_by_hosp[hospital_id]:
            doc_id = random.choice(doc_by_hosp[hospital_id])
        else:
            doc_id = random.choice(doctor_ids)

        # 6. v2: LOS based on hospital profile + department + severity + admission_type
        h_los_mult, h_readmit_base, h_mort_base = hospital_clinical_profiles.get(hospital_id, (1.0, 0.08, 0.08))

        if adm_type == "Day-care":
            los = 1
        else:
            los_min, los_mode, los_max = dept_los_params.get(dept, (2, 5, 14))
            base_los = int(np.random.triangular(los_min, los_mode, los_max))
            m_los_mult = month_los_mult.get(month, 1.0)
            mult = severity_los_mult.get(severity, 1.0) * h_los_mult * m_los_mult
            los = max(1, int(round(base_los * mult)))
            los = min(los, 35)

        dis_date = adm_date + timedelta(days=los)

        # 7. v2: Ward type based on severity
        ward_w = severity_ward_weights.get(severity, [0.40, 0.25, 0.25, 0.10])
        ward   = random.choices(ward_types, weights=ward_w, k=1)[0]

        # 8. v2: Discharge type based on hospital mortality profile & severity
        outcomes = severity_outcomes.get(severity, severity_outcomes["Moderate"])
        mort_scale = h_mort_base / 0.08
        exp_prob = outcomes["expired"] * mort_scale
        lama_prob = outcomes["lama"]
        ref_prob = outcomes["referred"]
        rec_prob = max(0.1, 1.0 - (exp_prob + lama_prob + ref_prob))

        discharge = random.choices(
            ["Recovered", "LAMA", "Referred", "Expired"],
            weights=[rec_prob, lama_prob, ref_prob, exp_prob],
            k=1
        )[0]

        # 9. v2: Readmission based on hospital quality profile & severity
        readmit_scale = h_readmit_base / 0.08
        readmit_chance = min(0.35, outcomes["readmission"] * readmit_scale)
        readmission = random.random() < readmit_chance

        # 10. v3: Gender-biased patient selection by department
        gw = dept_gender_weights.get(dept, default_gender_wt)
        pool_idx = random.choices([0, 1, 2], weights=gw, k=1)[0]
        selected_pool = gender_pools[pool_idx]
        patient_id = random.choice(selected_pool) if selected_pool else random.choice(patient_ids)

        rows.append({
            "admission_id"   : f"ADM-{str(i).zfill(7)}",
            "patient_id"     : patient_id,
            "doctor_id"      : doc_id,
            "hospital_id"    : hospital_id,
            "icd_code"       : icd_code,
            "admission_date" : adm_date.date(),
            "discharge_date" : dis_date.date(),
            "admission_type" : adm_type,
            "ward_type"      : ward,
            "department"     : dept,
            "bed_id"         : f"BED-{random.randint(1,650):04d}",
            "length_of_stay" : los,
            "discharge_type" : discharge,
            "readmission_flag": readmission,
            "quarter"        : quarter,
            "fiscal_year"    : "FY2024-25",
        })

    df = pd.DataFrame(rows)

    # ── Dirty data (SAME as v1 — preserving all injections) ───────────────
    # discharge before admission (~1%)
    bad_idx = random.sample(range(n), int(n * 0.01))
    for i in bad_idx:
        df.at[i, "discharge_date"] = (
            pd.to_datetime(df.at[i, "admission_date"]) - timedelta(days=random.randint(1,5))
        ).date()

    # null bed_id (~3%)
    null_bed_idx = random.sample(range(n), int(n * 0.03))
    for i in null_bed_idx:
        df.at[i, "bed_id"] = None

    # duplicate admission_ids (~0.5%)
    dup_idx = random.sample(range(n), int(n * 0.005))
    dups = df.iloc[dup_idx].copy()
    df = pd.concat([df, dups], ignore_index=True)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 6.  FACT_BILLING  (~120 000 rows) — v2: Tier/region pricing + metro payer mix
# ─────────────────────────────────────────────────────────────────────────────

def generate_fact_billing(admissions_df: pd.DataFrame,
                          hospitals_df: pd.DataFrame) -> pd.DataFrame:

    # ── v2: Hospital pricing lookup (tier × region multiplier) ────────────
    tier_mult   = {"Tier-1": 1.30, "Tier-2": 0.80}
    region_mult = {"South": 1.10, "West": 1.10, "North": 0.95, "East": 0.90}
    hosp_price_mult = {}
    for _, h in hospitals_df.iterrows():
        t = tier_mult.get(h["tier"], 1.0)
        r = region_mult.get(h["region"], 1.0)
        hosp_price_mult[h["hospital_id"]] = t * r

    # ── v2: Hospital tier lookup for payer mix ────────────────────────────
    hosp_tier = hospitals_df.set_index("hospital_id")["tier"].to_dict()

    # ── v2: Department-based charge multiplier ────────────────────────────
    dept_charge_mult = {
        "Cardiac Sciences":      1.50,
        "Cancer Care":           1.40,
        "Neurosciences":         1.30,
        "Critical Care":         1.40,
        "Surgery":               1.20,
        "Bone & Joint":          1.10,
        "Renal Sciences":        1.10,
        "Respiratory":           1.00,
        "Digestive Health":      1.00,
        "Diabetes & Endocrine":  0.90,
        "Women & Child":         0.90,
        "Emergency & Trauma":    1.10,
        "ENT":                   0.70,
        "Eye Care":              0.60,
        "Diagnostics":           0.50,
    }

    payer_types    = ["Self-Pay","Cashless","Reimbursement","Corporate TPA","Government"]
    # v2: Metro vs Tier-2 payer weights (metros have more cashless/corporate)
    metro_payer_w  = [0.20, 0.35, 0.15, 0.22, 0.08]
    tier2_payer_w  = [0.38, 0.22, 0.15, 0.12, 0.13]
    ins_companies  = ["Star Health","HDFC Ergo","Niva Bupa","Care Health",
                      "New India Assurance","United India","Oriental Insurance",None]
    tpa_names      = ["Paramount TPA","Medi Assist","HealthIndia TPA","Vidal Health",
                      "Good Health TPA",None,None]
    pay_statuses   = ["Paid","Paid","Paid","Partial","Pending","Written-off"]

    # ── v3: Monthly revenue seasonality multiplier ──────────────────────────
    month_revenue_mult = {
        1: 1.08, 2: 0.94, 3: 1.06, 4: 0.90, 5: 0.92, 6: 0.88,
        7: 1.03, 8: 1.00, 9: 0.95, 10: 1.04, 11: 1.06, 12: 1.10,
    }

    # ── v3.1: Monthly payer weights shift (Corporate/Cashless surges in Mar & Dec; Self-Pay in Summer/Monsoon) ──
    # Format: month -> [Self-Pay, Cashless, Reimbursement, Corporate TPA, Government]
    month_payer_shift = {
        1:  {"metro": [0.18, 0.35, 0.15, 0.24, 0.08], "tier2": [0.35, 0.22, 0.15, 0.14, 0.14]},
        2:  {"metro": [0.22, 0.32, 0.16, 0.20, 0.10], "tier2": [0.40, 0.20, 0.15, 0.12, 0.13]},
        3:  {"metro": [0.10, 0.42, 0.12, 0.30, 0.06], "tier2": [0.25, 0.30, 0.15, 0.20, 0.10]}, # FY-end rush
        4:  {"metro": [0.30, 0.28, 0.15, 0.17, 0.10], "tier2": [0.45, 0.18, 0.15, 0.10, 0.12]}, # Post-FY lull
        5:  {"metro": [0.32, 0.26, 0.15, 0.15, 0.12], "tier2": [0.48, 0.16, 0.14, 0.09, 0.13]}, # Summer self-pay
        6:  {"metro": [0.35, 0.25, 0.15, 0.14, 0.11], "tier2": [0.52, 0.15, 0.13, 0.08, 0.12]}, # Deep pre-monsoon
        7:  {"metro": [0.30, 0.28, 0.15, 0.15, 0.12], "tier2": [0.46, 0.18, 0.14, 0.10, 0.12]}, # Monsoon fever
        8:  {"metro": [0.28, 0.30, 0.15, 0.16, 0.11], "tier2": [0.44, 0.20, 0.14, 0.10, 0.12]},
        9:  {"metro": [0.24, 0.32, 0.15, 0.18, 0.11], "tier2": [0.38, 0.22, 0.14, 0.12, 0.14]},
        10: {"metro": [0.18, 0.35, 0.15, 0.22, 0.10], "tier2": [0.34, 0.24, 0.15, 0.14, 0.13]}, # Festive packages
        11: {"metro": [0.14, 0.38, 0.14, 0.26, 0.08], "tier2": [0.28, 0.28, 0.15, 0.17, 0.12]},
        12: {"metro": [0.08, 0.45, 0.11, 0.32, 0.04], "tier2": [0.20, 0.34, 0.15, 0.22, 0.09]}, # Year-end surge
    }

    # ── v3.1: Monthly discount campaign multiplier (seasonal health camps & negotiated tariffs) ─
    # Mar & Dec have high corporate volume discounts; Oct/Nov have festive health camp discounts
    month_disc_factor = {
        1: 1.10, 2: 0.95, 3: 1.35, 4: 0.70, 5: 0.65, 6: 0.58,
        7: 0.75, 8: 0.80, 9: 0.90, 10: 1.15, 11: 1.25, 12: 1.40,
    }

    # ── v3: Payer-specific base discount ranges (low, high) ───────────────
    payer_discount_range = {
        "Self-Pay":        (0.01, 0.05),    # Patients pay near-list price
        "Cashless":        (0.10, 0.18),    # Insurer-negotiated discounts
        "Reimbursement":   (0.01, 0.07),    # Patient pays, claims later
        "Corporate TPA":   (0.12, 0.22),    # Bulk corporate rates
        "Government":      (0.16, 0.26),    # CGHS/ECHS mandated deep discounts
    }

    # ── v3: Payer × Tier-specific collection rate ranges ──────────────────
    payer_collection_range = {
        "Self-Pay":        {"Tier-1": (0.72, 0.95), "Tier-2": (0.65, 0.92)},
        "Cashless":        {"Tier-1": (0.88, 1.00), "Tier-2": (0.82, 0.98)},
        "Reimbursement":   {"Tier-1": (0.78, 0.98), "Tier-2": (0.72, 0.95)},
        "Corporate TPA":   {"Tier-1": (0.90, 1.00), "Tier-2": (0.85, 0.98)},
        "Government":      {"Tier-1": (0.68, 0.90), "Tier-2": (0.60, 0.85)},
    }

    rows = []
    unique_adm = admissions_df.drop_duplicates("admission_id")
    for idx, row in enumerate(unique_adm.itertuples(), 1):
        # v2: Look up price multiplier for this hospital and department
        h_mult = hosp_price_mult.get(getattr(row, "hospital_id", 1), 1.0)
        d_mult = dept_charge_mult.get(getattr(row, "department", "Surgery"), 1.0)

        # v3: Apply monthly revenue seasonality
        adm_month = pd.to_datetime(getattr(row, "admission_date")).month
        m_mult = month_revenue_mult.get(adm_month, 1.0)
        price_mult = h_mult * d_mult * m_mult

        procedure = round(random.uniform(5000, 200000) * price_mult, 2)
        pharmacy  = round(random.uniform(1000, 50000)  * price_mult, 2)
        lab       = round(random.uniform(500,  30000)  * price_mult, 2)
        room_rate = {"General":2000,"Semi-Private":4000,"Private":7000,"ICU":15000}
        room      = room_rate.get(getattr(row, "ward_type", "General"), 2000) * getattr(row, "length_of_stay", 1)
        # v2: Room rate also scaled by tier (premium hospitals charge more per room-day)
        room      = int(room * h_mult)
        gross     = round(procedure + pharmacy + lab + room, 2)

        # v3.1: Dynamic monthly payer mix
        is_metro = hosp_tier.get(getattr(row, "hospital_id", 1)) == "Tier-1"
        monthly_payer_wts = month_payer_shift.get(adm_month, {}).get("metro" if is_metro else "tier2", metro_payer_w if is_metro else tier2_payer_w)
        payer = random.choices(payer_types, weights=monthly_payer_wts)[0]

        # v3.1: Payer-specific discount with seasonal campaign adjustment
        disc_lo, disc_hi = payer_discount_range.get(payer, (0.01, 0.15))
        m_disc = month_disc_factor.get(adm_month, 1.0)
        raw_disc_rate = random.uniform(disc_lo, disc_hi) * m_disc
        applied_disc_rate = max(0.005, min(0.35, raw_disc_rate))
        discount  = round(gross * applied_disc_rate, 2)
        net       = round(gross - discount, 2)

        # v3: Payer × Tier-specific collection rate
        tier_key = "Tier-1" if is_metro else "Tier-2"
        coll_lo, coll_hi = payer_collection_range.get(payer, {}).get(tier_key, (0.65, 0.95))
        collected = round(net * random.uniform(coll_lo, coll_hi), 2)
        outstanding = round(max(0, net - collected), 2)

        # v3: Variable billing lag (days after discharge)
        los = getattr(row, "length_of_stay", 3)
        ward = getattr(row, "ward_type", "General")
        if getattr(row, "admission_type", "Elective") == "Day-care":
            bill_lag = random.choices([0, 1], weights=[0.7, 0.3], k=1)[0]
        elif ward == "ICU" or los > 10:
            bill_lag = random.randint(2, 7)
        elif los > 5:
            bill_lag = random.randint(1, 4)
        else:
            bill_lag = random.randint(0, 2)
        # Tier-2 hospitals have slower billing teams
        if not is_metro:
            bill_lag += random.choices([0, 1, 2], weights=[0.5, 0.35, 0.15], k=1)[0]
        billing_date = (pd.to_datetime(getattr(row, "discharge_date")) + timedelta(days=bill_lag)).date()

        rows.append({
            "bill_id"            : f"BILL-{str(idx).zfill(7)}",
            "admission_id"       : row.admission_id,
            "hospital_id"        : row.hospital_id,
            "gross_amount"       : gross,
            "discount_amount"    : discount,
            "net_amount"         : net,
            "collected_amount"   : collected,
            "outstanding_amount" : outstanding,
            "payer_type"         : payer,
            "insurance_company"  : random.choice(ins_companies),
            "tpa_name"           : random.choice(tpa_names),
            "billing_date"       : billing_date,
            "payment_status"     : random.choice(pay_statuses),
            "procedure_charges"  : procedure,
            "pharmacy_charges"   : pharmacy,
            "lab_charges"        : lab,
            "room_charges"       : room,
        })

    df = pd.DataFrame(rows)

    # ── Dirty: collected > net (~2%) — SAME as v1 ─────────────────────────
    bad_idx = random.sample(range(len(df)), int(len(df) * 0.02))
    for i in bad_idx:
        df.at[i, "collected_amount"] = df.at[i, "net_amount"] * random.uniform(1.01, 1.20)

    # ── Dirty: null insurance_company for cashless rows (~4%) — SAME as v1
    cashless_mask = df["payer_type"] == "Cashless"
    cashless_idx  = df[cashless_mask].index.tolist()
    null_ins_idx  = random.sample(cashless_idx, int(len(cashless_idx) * 0.04))
    df.loc[null_ins_idx, "insurance_company"] = None

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 7.  FACT_LAB_ORDERS  (~200 000 rows) — v2: Weighted by ward type
# ─────────────────────────────────────────────────────────────────────────────

def generate_fact_lab_orders(admissions_df: pd.DataFrame, n_total: int = 200_000) -> pd.DataFrame:
    test_catalog = [
        ("Complete Blood Count (CBC)",   "Pathology",   4,  500),
        ("Liver Function Test (LFT)",    "Pathology",   6,  800),
        ("Kidney Function Test (KFT)",   "Pathology",   6,  750),
        ("Blood Glucose Fasting",        "Pathology",   3,  300),
        ("HbA1c",                        "Pathology",   8, 1200),
        ("Lipid Profile",                "Pathology",   8,  900),
        ("Thyroid Profile (T3/T4/TSH)",  "Pathology",  10, 1100),
        ("Urine Routine",                "Pathology",   4,  400),
        ("Blood Culture",                "Microbiology",48, 1500),
        ("ECG",                          "Cardiology",   1,  600),
        ("2D Echo",                      "Cardiology",  12, 4000),
        ("Chest X-Ray",                  "Radiology",   3, 1200),
        ("CT Scan Abdomen",              "Radiology",  12, 8000),
        ("MRI Brain",                    "Radiology",  24,15000),
        ("Ultrasound Abdomen",           "Radiology",   6, 3500),
        ("Troponin I",                   "Pathology",   3, 1800),
        ("PT/INR",                       "Pathology",   4,  600),
        ("Serum Electrolytes",           "Pathology",   4,  700),
        ("Dengue NS1 Antigen",           "Serology",    6, 1200),
        ("Malaria Antigen Test",         "Serology",    4,  800),
    ]

    admission_ids  = admissions_df["admission_id"].tolist()
    hospital_ids   = admissions_df["hospital_id"].tolist()
    adm_dates      = admissions_df["admission_date"].tolist()

    # ── v3: Test-specific result status distributions ─────────────────────
    # Format: test_name → [Normal_wt, Abnormal_wt, Critical_wt]
    test_result_profiles = {
        # Routine screening — mostly normal
        "Complete Blood Count (CBC)":    [0.70, 0.25, 0.05],
        "Urine Routine":                 [0.72, 0.23, 0.05],
        "Blood Glucose Fasting":         [0.60, 0.30, 0.10],
        "Lipid Profile":                 [0.55, 0.35, 0.10],
        "Thyroid Profile (T3/T4/TSH)":   [0.65, 0.28, 0.07],
        "HbA1c":                         [0.50, 0.38, 0.12],
        # Liver/kidney — moderate abnormal
        "Liver Function Test (LFT)":     [0.55, 0.32, 0.13],
        "Kidney Function Test (KFT)":    [0.52, 0.33, 0.15],
        "Serum Electrolytes":            [0.58, 0.30, 0.12],
        "PT/INR":                        [0.50, 0.35, 0.15],
        # Cardiac markers — high critical
        "Troponin I":                    [0.40, 0.35, 0.25],
        "ECG":                           [0.45, 0.35, 0.20],
        "2D Echo":                       [0.40, 0.38, 0.22],
        # Culture/serology — moderate
        "Blood Culture":                 [0.55, 0.30, 0.15],
        "Dengue NS1 Antigen":            [0.50, 0.35, 0.15],
        "Malaria Antigen Test":          [0.60, 0.28, 0.12],
        # Imaging — high abnormal (ordered when symptomatic)
        "Chest X-Ray":                   [0.42, 0.40, 0.18],
        "CT Scan Abdomen":               [0.35, 0.45, 0.20],
        "MRI Brain":                     [0.30, 0.45, 0.25],
        "Ultrasound Abdomen":            [0.45, 0.38, 0.17],
    }
    default_result_wts = [0.50, 0.35, 0.15]
    result_labels = ["Normal", "Abnormal", "Critical"]

    # ── v2: Weight admission selection by ward type (ICU → more tests) ────
    ward_intensity  = {"ICU": 3.0, "Private": 1.5, "Semi-Private": 1.2, "General": 1.0}
    ward_types_list = admissions_df["ward_type"].tolist()
    intensity_wts   = [ward_intensity.get(wt, 1.0) for wt in ward_types_list]

    # Pre-compute all weighted indices for performance
    selected_indices = random.choices(range(len(admission_ids)),
                                      weights=intensity_wts, k=n_total)

    rows = []
    for i in range(1, n_total + 1):
        idx           = selected_indices[i - 1]   # v2: weighted, not uniform
        test          = random.choice(test_catalog)
        adm_dt        = pd.to_datetime(adm_dates[idx])
        sample_dt     = adm_dt + timedelta(hours=random.randint(1, 24))
        expected_tat  = test[2]
        tat_actual    = max(0.5, np.random.normal(expected_tat, expected_tat * 0.25))
        report_dt     = sample_dt + timedelta(hours=tat_actual)
        breach        = tat_actual > expected_tat * 1.20

        # v3: Test-specific result status
        result_wts = test_result_profiles.get(test[0], default_result_wts)
        result_status = random.choices(result_labels, weights=result_wts, k=1)[0]

        rows.append({
            "lab_order_id"       : f"LAB-{str(i).zfill(7)}",
            "admission_id"       : admission_ids[idx],
            "hospital_id"        : hospital_ids[idx],
            "test_name"          : test[0],
            "test_category"      : test[1],
            "order_datetime"     : sample_dt - timedelta(minutes=random.randint(5,60)),
            "sample_collected_dt": sample_dt,
            "report_delivered_dt": report_dt,
            "tat_hours"          : round(tat_actual, 2),
            "tat_breach_flag"    : breach,
            "test_cost"          : test[3],
            "result_status"      : result_status,
        })

    df = pd.DataFrame(rows)

    # ── Dirty: report before sample (~1.5%) — SAME as v1 ─────────────────
    bad_idx = random.sample(range(n_total), int(n_total * 0.015))
    for i in bad_idx:
        df.at[i, "report_delivered_dt"] = (
            pd.to_datetime(df.at[i, "sample_collected_dt"]) - timedelta(hours=random.randint(1,5))
        )

    # ── Dirty: missing TAT (~2%) — SAME as v1 ────────────────────────────
    null_tat_idx = random.sample(range(n_total), int(n_total * 0.02))
    df.loc[null_tat_idx, "tat_hours"] = None

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 8.  FACT_PHARMACY_ORDERS  (~180 000 rows) — v2: Weighted + tier-based stockout
# ─────────────────────────────────────────────────────────────────────────────

def generate_fact_pharmacy_orders(admissions_df: pd.DataFrame,
                                   n_total: int = 180_000) -> pd.DataFrame:
    drug_catalog = [
        ("Paracetamol 500mg",      "Analgesic",        5),
        ("Ibuprofen 400mg",        "Analgesic",        8),
        ("Amoxicillin 500mg",      "Antibiotic",      25),
        ("Azithromycin 500mg",     "Antibiotic",      45),
        ("Metformin 500mg",        "Antidiabetic",    12),
        ("Insulin Glargine",       "Antidiabetic",   180),
        ("Atorvastatin 40mg",      "Cardiac",         30),
        ("Amlodipine 5mg",         "Antihypertensive",18),
        ("Losartan 50mg",          "Antihypertensive",22),
        ("Pantoprazole 40mg",      "GI",              15),
        ("Ondansetron 4mg",        "Antiemetic",      20),
        ("Ceftriaxone 1g Inj",     "Antibiotic",     120),
        ("Piperacillin-Tazobactam","Antibiotic",     350),
        ("Heparin 5000IU",         "Anticoagulant",   90),
        ("Enoxaparin 40mg",        "Anticoagulant",  160),
        ("Furosemide 40mg",        "Diuretic",        10),
        ("Spironolactone 25mg",    "Diuretic",        20),
        ("Salbutamol Inhaler",     "Respiratory",     85),
        ("Budesonide Inhaler",     "Respiratory",    180),
        ("Morphine 10mg Inj",      "Analgesic",       95),
        ("Dexamethasone 4mg",      "Steroid",         35),
        ("Methylprednisolone",     "Steroid",        120),
        ("Ondansetron 8mg Inj",    "Antiemetic",      40),
        ("Clexane 60mg",           "Anticoagulant",  230),
        ("Normal Saline 500ml",    "IV Fluid",        45),
        ("Ringer Lactate 500ml",   "IV Fluid",        50),
        ("Dextrose 5% 500ml",      "IV Fluid",        55),
        ("Vancomycin 500mg",       "Antibiotic",     480),
        ("Meropenem 1g",           "Antibiotic",     650),
        ("Albumin 20% 100ml",      "Blood Product", 2200),
    ]

    admission_ids = admissions_df["admission_id"].tolist()
    hospital_ids  = admissions_df["hospital_id"].tolist()
    adm_dates     = admissions_df["admission_date"].tolist()

    # ── v2: Weight admission selection by ward type (ICU → more drugs) ────
    ward_intensity  = {"ICU": 3.0, "Private": 1.5, "Semi-Private": 1.2, "General": 1.0}
    ward_types_list = admissions_df["ward_type"].tolist()
    intensity_wts   = [ward_intensity.get(wt, 1.0) for wt in ward_types_list]

    # Pre-compute all weighted indices for performance
    selected_indices = random.choices(range(len(admission_ids)),
                                      weights=intensity_wts, k=n_total)

    rows = []
    for i in range(1, n_total + 1):
        idx         = selected_indices[i - 1]   # v2: weighted, not uniform
        drug        = random.choice(drug_catalog)
        qty_ordered = random.randint(1, 30)
        # v2: Tier-2 hospitals have higher stockout due to supply chain gaps
        is_metro    = hospital_ids[idx] <= 8
        stockout    = random.random() < (0.02 if is_metro else 0.05)
        qty_disp    = 0 if stockout else qty_ordered
        adm_dt      = pd.to_datetime(adm_dates[idx])
        order_dt    = adm_dt + timedelta(hours=random.randint(1,48))
        disp_dt     = order_dt + timedelta(hours=random.randint(0,4))
        expiry      = (datetime(2024,12,31) + timedelta(days=random.randint(30,730))).date()
        wastage     = (not stockout) and (random.random() < 0.04)

        rows.append({
            "pharmacy_order_id" : f"RX-{str(i).zfill(7)}",
            "admission_id"      : admission_ids[idx],
            "hospital_id"       : hospital_ids[idx],
            "drug_name"         : drug[0],
            "drug_category"     : drug[1],
            "quantity_ordered"  : qty_ordered,
            "quantity_dispensed": qty_disp,
            "unit_cost"         : drug[2],
            "total_cost"        : round(qty_disp * drug[2], 2),
            "order_date"        : order_dt.date(),
            "dispensed_date"    : disp_dt.date(),
            "stockout_flag"     : stockout,
            "expiry_date"       : expiry,
            "wastage_flag"      : wastage,
        })

    df = pd.DataFrame(rows)

    # ── Dirty: qty_dispensed > qty_ordered (~1%) — SAME as v1 ─────────────
    bad_idx = random.sample(range(n_total), int(n_total * 0.01))
    for i in bad_idx:
        df.at[i, "quantity_dispensed"] = df.at[i, "quantity_ordered"] + random.randint(1,10)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# 9.  FACT_PATIENT_FEEDBACK  (~40 000 rows) — v2: Hospital CSAT personality
# ─────────────────────────────────────────────────────────────────────────────

def generate_fact_patient_feedback(admissions_df: pd.DataFrame,
                                    hospitals_df: pd.DataFrame,
                                    n: int = 40_000) -> pd.DataFrame:

    # ── v2: Hospital-specific base satisfaction scores ────────────────────
    hospital_csat_base = {
        1:  4.3,    # Bengaluru (NABH, est 2005)
        2:  4.5,    # Mumbai (JCI, est 2002) — premium flagship
        3:  4.0,    # Delhi (NABH, est 2001)
        4:  4.2,    # Chennai (NABH, est 2006)
        5:  3.8,    # Hyderabad (NABH, est 2008)
        6:  3.9,    # Pune (NABH, est 2010)
        7:  3.7,    # Kolkata (NABH, est 2004)
        8:  3.3,    # Ahmedabad (None, est 2009)
        9:  3.5,    # Jaipur (None, est 2012)
        10: 3.0,    # Lucknow (None, est 2013)
        11: 3.6,    # Bhubaneswar (NABH, est 2014)
        12: 3.2,    # Chandigarh (None, est 2015)
        13: 4.0,    # Kochi (NABH, est 2011) — Kerala healthcare
        14: 2.8,    # Indore (None, est 2016)
        15: 2.9,    # Nagpur (None, est 2017)
        16: 3.8,    # Coimbatore (None, est 2018)
        17: 3.1,    # Visakhapatnam (None, est 2015)
        18: 2.7,    # Patna (None, est 2019)
        19: 2.5,    # Guwahati (None, est 2020)
        20: 3.4,    # Thiruvananthapuram (None, est 2016)
        21: 3.0,    # Surat (None, est 2018)
        22: 2.9,    # Vadodara (None, est 2019)
        23: 2.6,    # Bhopal (None, est 2020)
        24: 2.8,    # Dehradun (None, est 2021)
        25: 2.4,    # Ranchi (None, est 2022) — newest, smallest
    }

    # ── v2: NPS range calibrated realistically to hospital CSAT base ─────
    def get_nps_range(csat_base):
        if csat_base >= 4.0:
            return (35, 95)    # Top flagships: Mean ~ +65
        elif csat_base >= 3.5:
            return (15, 75)    # Good performers: Mean ~ +45
        elif csat_base >= 3.0:
            return (0, 55)     # Moderate: Mean ~ +28
        else:
            return (-10, 40)   # Emerging branches: Mean ~ +15 (mostly positive, some detractors)

    complaint_cats = ["Staff Behaviour","Billing Dispute","Delay in Treatment",
                      "Hygiene","Food Quality","Doctor Availability",None,None,None]

    sampled = admissions_df.sample(n=min(n, len(admissions_df)), random_state=SEED).reset_index(drop=True)

    rows = []
    for idx, row in enumerate(sampled.itertuples(), 1):
        hosp_id    = row.hospital_id
        csat_base  = hospital_csat_base.get(hosp_id, 3.5)

        # v2: Generate overall CSAT around the hospital's base score
        overall = max(1, min(5, int(round(np.random.normal(csat_base, 0.8)))))

        # v2: Complaint rate inversely correlated with CSAT base
        complaint_prob = max(0.03, 0.25 - (csat_base * 0.04))
        complaint = random.random() < complaint_prob

        # v2: NPS correlated with hospital CSAT base
        nps_low, nps_high = get_nps_range(csat_base)
        nps_score = random.randint(nps_low, nps_high)

        survey_dt = (pd.to_datetime(row.discharge_date) + timedelta(days=random.randint(0,7))).date()

        rows.append({
            "feedback_id"        : f"FB-{str(idx).zfill(6)}",
            "admission_id"       : row.admission_id,
            "hospital_id"        : hosp_id,
            "doctor_id"          : row.doctor_id,
            "survey_date"        : survey_dt,
            "overall_csat"       : overall,
            "doctor_rating"      : max(1, overall + random.randint(-1,1)),
            "nursing_rating"     : max(1, overall + random.randint(-1,1)),
            "cleanliness_rating" : max(1, overall + random.randint(-1,1)),
            "food_rating"        : max(1, min(6, int(round(np.random.normal(csat_base - 0.3, 1.0))))),
            "billing_rating"     : max(1, overall + random.randint(-2,1)),
            "nps_score"          : nps_score,
            "complaint_raised"   : complaint,
            "complaint_category" : random.choice(complaint_cats) if complaint else None,
        })

    df = pd.DataFrame(rows)

    # ── Dirty: NPS out of range — SAME as v1 ─────────────────────────────
    bad_idx = random.sample(range(n), int(n * 0.01))
    for i in bad_idx:
        df.at[i, "nps_score"] = random.choice([-200, 150, 999])

    # ── Dirty: ratings = 0 (invalid) — SAME as v1 ────────────────────────
    zero_idx = random.sample(range(n), int(n * 0.008))
    for i in zero_idx:
        df.at[i, "overall_csat"] = 0

    # ── Dirty: survey_date before discharge_date — SAME as v1 ────────────
    merge_cols = admissions_df[["admission_id","discharge_date"]].drop_duplicates("admission_id")
    df = df.merge(merge_cols, on="admission_id", how="left")
    bad_survey = random.sample(range(n), int(n * 0.01))
    for i in bad_survey:
        if pd.notna(df.at[i, "discharge_date"]):
            df.at[i, "survey_date"] = (
                pd.to_datetime(df.at[i, "discharge_date"]) - timedelta(days=random.randint(1,5))
            ).date()
    df.drop(columns=["discharge_date"], inplace=True)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  PulseMetrics-Q  |  Data Generator (v3 — Full Non-Uniform)")
    print("  Generating 9 tables for pan-India hospital analytics")
    print("="*60 + "\n")

    print("-> Generating dimension tables...")
    hospitals = generate_dim_hospitals();   save(hospitals,  "dim_hospitals")
    patients  = generate_dim_patients();    save(patients,   "dim_patients")
    doctors   = generate_dim_doctors(hospitals); save(doctors,"dim_doctors")
    icd_codes = generate_dim_icd_codes();   save(icd_codes,  "dim_icd_codes")

    print("\n-> Generating fact tables (this may take ~2 minutes)...")
    admissions = generate_fact_admissions(patients, doctors, hospitals, icd_codes)
    save(admissions, "fact_admissions")

    billing    = generate_fact_billing(admissions, hospitals);   save(billing,   "fact_billing")
    lab        = generate_fact_lab_orders(admissions); save(lab,      "fact_lab_orders")
    pharmacy   = generate_fact_pharmacy_orders(admissions); save(pharmacy,"fact_pharmacy_orders")
    feedback   = generate_fact_patient_feedback(admissions, hospitals); save(feedback,"fact_patient_feedback")

    print("\n" + "="*60)
    print("  [SUCCESS] All 9 datasets saved to /data/raw/")
    print("  Next: open 01_data_generation.ipynb")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
