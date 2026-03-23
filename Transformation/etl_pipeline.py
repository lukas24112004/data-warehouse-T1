import schedule
import time
import importlib

import transformation1
import transformation2
import transformation3
import transformation4
import transformation5


def run_crm_cust():
    print("Running CRM customer job")
    try:
        importlib.reload(transformation1)
        transformation1.run()
    except Exception as e:
        print(f"CRM customer job failed: {e}")


def run_crm_prd():
    print("Running CRM product job")
    try:
        importlib.reload(transformation2)
        transformation2.run()
    except Exception as e:
        print(f"CRM product job failed: {e}")


def run_erp_cust():
    print("Running ERP customer job")
    try:
        importlib.reload(transformation3)
        transformation3.run()
    except Exception as e:
        print(f"ERP customer job failed: {e}")


def run_erp_loc():
    print("Running ERP location job")
    try:
        importlib.reload(transformation4)
        transformation4.run()
    except Exception as e:
        print(f"ERP location job failed: {e}")


def run_crm_sales():
    print("Running CRM sales job")
    try:
        importlib.reload(transformation5)
        transformation5.run()
    except Exception as e:
        print(f"CRM sales job failed: {e}")


# run once immediately
run_crm_cust()
run_crm_prd()
run_erp_cust()
run_erp_loc()
run_crm_sales()

# then schedule recurring runs
schedule.every().hour.do(run_crm_cust)
schedule.every().hour.do(run_crm_prd)
schedule.every().hour.do(run_erp_cust)
schedule.every().day.at("02:00").do(run_erp_loc)
schedule.every().day.at("03:00").do(run_crm_sales)

print("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(5)
