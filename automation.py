from playwright.sync_api import Playwright, sync_playwright, expect

URL=""
USER=""
PASSWORD=""
ACCOUNT_LIST=[] 
TARGETRESELLER=""

def run(playwright: Playwright) -> None:
    try:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(URL)
        page.locator("#inp_user").click()
        page.locator("#inp_user").fill(USER)
        page.locator("#inp_password").click()
        page.locator("#inp_password").fill(PASSWORD)
        page.get_by_role("button", name="Sign In").click()
        page.frame_locator("frame[name=\"topFrame\"]").get_by_role("link", name="Billing").click()
        
        for customerId in ACCOUNT_LIST:
            try:
                
                page.frame_locator("frame[name=\"leftFrame\"]").get_by_role("link", name="All Customers").click()
                page.frame_locator("frame[name=\"mainFrame\"]").locator("#filter_AccountID").click()
                page.frame_locator("frame[name=\"mainFrame\"]").locator("#filter_AccountID").fill(str(customerId))
                page.frame_locator("frame[name=\"mainFrame\"]").locator("#filter_AStatus").select_option("0")
                page.frame_locator("frame[name=\"mainFrame\"]").get_by_role("link", name="Search", exact=True).click()

                page.wait_for_timeout(3000)
                customers_filter_list = page.frame_locator("frame[name=\"mainFrame\"]").get_by_role("link", name=str(customerId))
                if customers_filter_list.count() == 0:
                    print(f"No Customer ID found for {customerId}")
                    continue
                else:  
                    customers_filter_list.click()

                page.frame_locator("frame[name=\"mainFrame\"]").get_by_role("button", name="Transfer to Another Distributor").click()
                page.wait_for_timeout(3000)
                #FIRST VIEW EXECUTION 
                with page.expect_popup() as page1_info:
                    page.frame_locator("frame[name=\"mainFrame\"]").locator("#input___refvTgtResellerAccount").click()
                page1 = page1_info.value

                page1.locator("#filter_AccountID").click()
                page1.locator("#filter_AccountID").fill(TARGETRESELLER)
                page1.get_by_role("link", name="Search", exact=True).click()
                page.wait_for_timeout(3000)
                #CONDITION IF RESELLER ID IS NOT FOUND
                reseller_filter_list = page1.get_by_role("cell", name=TARGETRESELLER)
                if reseller_filter_list.count() == 0:
                    print(f"No Reseller ID found for {customerId}")
                    page1.close()
                    continue
                else:
                    page1.get_by_role("cell", name=TARGETRESELLER).click()
                    page1.close()
                    
                 
                page.frame_locator("frame[name=\"mainFrame\"]").get_by_role("button", name="Next").click()
                transfer_button = page.frame_locator("frame[name=\"mainFrame\"]").get_by_role("button[name=\"Transfer\"]")
                if transfer_button:
                    transfer_button.click()
                    print(f"Customer {customerId}: Transferred")
                else:
                    errors_message = page.frame_locator("frame[name=\"mainFrame\"]").locator("#error_text")
                    page.wait_for_timeout(3000)
                    if errors_message:
                        page.frame_locator("frame[name=\"mainFrame\"]").get_by_role("button", name="Cancel").click()
                        print(f"ERROR: Customer {customerId}: {errors_message.inner_text()}")
                        continue
                
            except Exception as e:
                print(e)

        context.close()
        browser.close()
    except Exception as e:
        print(e)
        

with sync_playwright() as playwright:
    run(playwright)
