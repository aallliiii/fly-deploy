from datetime import datetime

def prepare_event_text(row_dict: dict) -> str:
    def safe_str(value):
        return str(value) if value is not None and str(value).strip() != "" else None
    
    def weekDay(date):
        return datetime.strptime(date, "%d/%m/%Y").strftime("%A")
    
    def isWeekend(date):
        weekendorNot = datetime.strptime(date, "%d/%m/%Y").strftime("%A") in ["Saturday", "Sunday"]
        if weekendorNot:
            return "weekend"
        else:
            return "workday"
    
    text_parts = []
    
    if safe_str(row_dict.get('name')) and safe_str(row_dict.get('description')):
        text_parts.append(f"This is an event called {safe_str(row_dict.get('name'))} which is described as {safe_str(row_dict.get('description'))}.")
    elif safe_str(row_dict.get('name')):
        text_parts.append(f"This is an event called {safe_str(row_dict.get('name'))}.")
    
    if safe_str(row_dict.get('start_date')) and safe_str(row_dict.get('start_time')) and safe_str(row_dict.get('end_date')) and safe_str(row_dict.get('end_time')):
        text_parts.append(f"The event starts on {safe_str(row_dict.get('start_date'))} at {safe_str(row_dict.get('start_time'))} and ends on {safe_str(row_dict.get('end_date'))} at {safe_str(row_dict.get('end_time'))}.")
    elif safe_str(row_dict.get('start_date')) and safe_str(row_dict.get('start_time')):
        text_parts.append(f"The event starts on {safe_str(row_dict.get('start_date'))} at {safe_str(row_dict.get('start_time'))}.")
    elif safe_str(row_dict.get('start_date')):
        text_parts.append(f"The event is on {safe_str(row_dict.get('start_date'))}.")
    
    if safe_str(row_dict.get('start_date')):
        try:
            event_day = weekDay(row_dict.get('start_date'))
            event_timing = isWeekend(row_dict.get('start_date'))
            text_parts.append(f"It takes place on a {event_day} during {event_timing}.")
        except:
            pass
    
    location_parts = []
    if safe_str(row_dict.get('address')):
        location_parts.append(safe_str(row_dict.get('address')))
    if safe_str(row_dict.get('city')):
        location_parts.append(safe_str(row_dict.get('city')))
    if safe_str(row_dict.get('state')):
        location_parts.append(safe_str(row_dict.get('state')))
    if safe_str(row_dict.get('country')):
        location_parts.append(safe_str(row_dict.get('country')))
    
    if location_parts:
        location_text = "The venue is located at " + ", ".join(location_parts)
        if safe_str(row_dict.get('zip_code')):
            location_text += f" with zip code {safe_str(row_dict.get('zip_code'))}"
        text_parts.append(location_text + ".")
    
    if safe_str(row_dict.get('ticket_price')):
        text_parts.append(f"Tickets are priced at £{safe_str(row_dict.get('ticket_price'))}.")
    
    if safe_str(row_dict.get('groups')):
        text_parts.append(f"The event is for {safe_str(row_dict.get('groups'))} age group.")
    
    if safe_str(row_dict.get('types_name')):
        text_parts.append(f"This event falls under the {safe_str(row_dict.get('types_name'))} category.")
    
    if safe_str(row_dict.get('status')):
        text_parts.append(f"It has a status of {safe_str(row_dict.get('status'))}.")
    
    if safe_str(row_dict.get('genre')):
        text_parts.append(f"The genre is {safe_str(row_dict.get('genre'))}.")
    
    audience_parts = []
    if safe_str(row_dict.get('audience')):
        audience_parts.append(f"designed for {safe_str(row_dict.get('audience'))} audience")
    if safe_str(row_dict.get('age_restriction')):
        audience_parts.append(f"age restriction of {safe_str(row_dict.get('age_restriction'))}")
    
    if audience_parts:
        text_parts.append(f"It is {' with '.join(audience_parts)}.")
    
    if safe_str(row_dict.get('features')):
        text_parts.append(f"Special features include {safe_str(row_dict.get('features'))}.")
    
    if safe_str(row_dict.get('indoor_outdoor')):
        text_parts.append(f"It is an {safe_str(row_dict.get('indoor_outdoor'))} event.")
    
    if safe_str(row_dict.get('dress_code')):
        text_parts.append(f"The dress code is {safe_str(row_dict.get('dress_code'))}.")
    
    if safe_str(row_dict.get('language')):
        text_parts.append(f"The event will be conducted in {safe_str(row_dict.get('language'))} language.")
    
    if safe_str(row_dict.get('season')):
        text_parts.append(f"This event is suitable for the {safe_str(row_dict.get('season'))} season.")
    
    if safe_str(row_dict.get('tags')):
        text_parts.append(f"It is tagged with {safe_str(row_dict.get('tags'))}.")
    
    return " ".join(text_parts)

def prepare_product_text(row_dict: dict) -> str:
    def safe_str(value):
        return str(value) if value is not None and str(value).strip() != "" else None
    
    text_parts = []
    
    if safe_str(row_dict.get('product_name')) and safe_str(row_dict.get('product_description')):
        text_parts.append(f"This is a product named {safe_str(row_dict.get('product_name'))} which is {safe_str(row_dict.get('product_description'))}.")
    elif safe_str(row_dict.get('product_name')):
        text_parts.append(f"This is a product named {safe_str(row_dict.get('product_name'))}.")
    
    if safe_str(row_dict.get('category_name')):
        text_parts.append(f"It belongs to the {safe_str(row_dict.get('category_name'))} category.")
    
    if safe_str(row_dict.get('brand_name')):
        text_parts.append(f"It is manufactured by the brand {safe_str(row_dict.get('brand_name'))}.")
    
    if safe_str(row_dict.get('type_name')):
        text_parts.append(f"The product type is {safe_str(row_dict.get('type_name'))}.")
    
    if safe_str(row_dict.get('color')):
        text_parts.append(f"It comes in {safe_str(row_dict.get('color'))} color.")
    
    if safe_str(row_dict.get('material')):
        text_parts.append(f"It is made from {safe_str(row_dict.get('material'))} material.")
    
    if safe_str(row_dict.get('style')):
        text_parts.append(f"It features a {safe_str(row_dict.get('style'))} style.")
    
    if safe_str(row_dict.get('occasion')):
        text_parts.append(f"This product is perfect for {safe_str(row_dict.get('occasion'))} occasions.")
    
    if safe_str(row_dict.get('fit')):
        text_parts.append(f"It offers a {safe_str(row_dict.get('fit'))} fit.")
    
    if safe_str(row_dict.get('pattern')):
        text_parts.append(f"The design includes a {safe_str(row_dict.get('pattern'))} pattern.")
    
    if safe_str(row_dict.get('season')):
        text_parts.append(f"It is ideal for the {safe_str(row_dict.get('season'))} season.")
    
    if safe_str(row_dict.get('audience')):
        text_parts.append(f"It is targeted towards {safe_str(row_dict.get('audience'))} audience.")
    
    if safe_str(row_dict.get('special_features')):
        text_parts.append(f"It includes special features such as {safe_str(row_dict.get('special_features'))}.")
    
    if safe_str(row_dict.get('tags')):
        text_parts.append(f"The product is tagged with {safe_str(row_dict.get('tags'))}.")
    
    return " ".join(text_parts)