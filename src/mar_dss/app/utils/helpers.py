from datetime import datetime
def parse_unknown_date(date_string):
    formats = [
        "%Y-%m-%d",      # 2022-10-15
        "%m/%d/%Y",      # 10/15/2022
        "%d/%m/%Y",      # 15/10/2022
        "%Y/%m/%d",      # 2022/10/15
        "%d-%m-%Y",      # 15-10-2022
        "%m-%d-%Y",      # 10-15-2022
        "%b %d, %Y",     # Oct 15, 2022
        "%B %d, %Y",     # October 15, 2022
        "%d %b %Y",      # 15 Oct 2022
        "%d %B %Y",      # 15 October 2022
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    # If no format works, return None or raise error
    return None