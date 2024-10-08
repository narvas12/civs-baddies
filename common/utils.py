from .enums import RatingTag
import requests


def format_rating_records(records):
    for r in records:
                if r.rating_type == 1:
                    r.rating_description =  RatingTag(r.rating_type).name
                elif r.rating_type == 2:
                    r.rating_description = RatingTag(r.rating_type).name
                elif r.rating_type == 3:
                    r.rating_description =  RatingTag(r.rating_type).name
                elif r.rating_type == 4:
                     r.rating_description = RatingTag(r.rating_type).name
                elif r.rating_type == 5:
                     r.rating_description = RatingTag(r.rating_type).name
                    
    return records





def get_conversion_rate(base_currency, target_currency, api_key):
    url = f"http://data.fixer.io/api/latest?access_key={api_key}&base={base_currency}&symbols={target_currency}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200 and data.get("success"):
        return data['rates'].get(target_currency, 1)
    return 1

def get_user_currency(ip_address, geolocation_api_key):
    url = f"https://ipinfo.io/{ip_address}/json?token={geolocation_api_key}"
    response = requests.get(url)
    data = response.json()
    country_code = data.get('country')
    

    country_currency_map = {
        'US': 'USD',
        'GB': 'GBP',
        'EU': 'EUR',
        'CA': 'CAD',
        'JP': 'JPY',
        'CN': 'CNY',
        'IN': 'INR',
        'BR': 'BRL',
        'RU': 'RUB',
        'DE': 'EUR',
        'FR': 'EUR',
        'IT': 'EUR',
        'ES': 'EUR',
        'AU': 'AUD',
        'NZ': 'NZD',
        'ZA': 'ZAR',
        'MX': 'MXN',
        'KR': 'KRW',
        'TH': 'THB',
        'ID': 'IDR',
        'PH': 'PHP',
        'VN': 'VND',
        'MY': 'MYR',
        'SG': 'SGD',
        'HK': 'HKD',
        'TW': 'TWD',
        'AE': 'AED',
        'SA': 'SAR',
        'IL': 'ILS',
        'TR': 'TRY',
        'EG': 'EGP',
        'NG': 'NGN',
        'KE': 'KES',
        'GH': 'GHS',
        'ZA': 'ZAR',
        'CO': 'COP',
        'AR': 'ARS',
        'CL': 'CLP',
        'PE': 'PEN',
        'EC': 'USD',
        'BO': 'BOB',
        'PY': 'PYG',
        'UY': 'UYU',
        'PA': 'PAB',
        'CR': 'CRC',
        'NI': 'NIO',
        'HN': 'HNL',
        'SV': 'SVC',
        'GT': 'GTQ',
        'BE': 'EUR',
        'NL': 'EUR',
        'DK': 'DKK',
        'SE': 'SEK',
        'NO': 'NOK',
        'FI': 'EUR',
        'CH': 'CHF',
        'AT': 'EUR',
        'CZ': 'CZK',
        'PL': 'PLN',
        'HU': 'HUF',
        'RO': 'RON',
        'BG': 'BGN',
        'RS': 'RSD',
        'ME': 'EUR',
        'MK': 'MKD',
        'AL': 'ALL',
        'GR': 'EUR',
        'CY': 'EUR',
        'LT': 'EUR',
        'LV': 'EUR',
        'EE': 'EUR',
        'MD': 'MDL',
        'UA': 'UAH',
        'BY': 'BYN',
        'KZ': 'KZT',
        'UZ': 'UZS',
        'TJ': 'TJS',
        'KG': 'KGS',
        'TM': 'TMT',
        'AZ': 'AZN',
        'GE': 'GEL',
        'AM': 'AMD',
        'SY': 'SYP',
        'IQ': 'IQD',
        'IR': 'IRR',
        'AF': 'AFN',
        'PK': 'PKR',
        'BD': 'BDT',
        'NP': 'NPR',
        'SL': 'LKR',
        'MV': 'MVR',
        'ML': 'MGA',
        'BF': 'XOF',
        'CI': 'XOF',
        'TG': 'XOF',
        'BJ': 'XOF',
        'NE': 'XOF',
        'MR': 'MRO',
        'SN': 'XOF',
        'GM': 'GMD',
        'GW': 'XOF',
        'ST': 'STN',
        'GQ': 'XAF',
        'GA': 'XAF',
        'CM': 'XAF',
        'CG': 'XAF',
        'CF': 'XAF',
        'TD': 'XAF',
        'LY': 'LYD',
        'TN': 'TND',
        'DZ': 'DZD',
        'MA': 'MAD',
        'MO': 'MOP',
        'LA': 'LAK',
        'MY': 'MYR',
        'SG': 'SGD',
        'PH': 'PHP',
        'ID': 'IDR',
        'VN': 'VND',
        'TH': 'THB',
        'KH': 'KHR',
        'MM': 'MMK',
        'BN': 'BND',
        'IN': 'INR',
        'NP': 'NPR',
        'BD': 'BDT',
        'PK': 'PKR',
        'AF': 'AFN',
        'TJ': 'TJS',
        'UZ': 'UZS',
        'KG': 'KGS',
        'TM': 'TMT',
        'AZ': 'AZN',
        'GE': 'GEL',
        'AM': 'AMD',
        'SY': 'SYP',
        'IQ': 'IQD',
        'IR': 'IRR',
        'KW': 'KWD',
        'BH': 'BHD',
        'OM': 'OMR',
        'QA': 'QAR',
        'YE': 'YER',
        'SD': 'SDG',
        'SS': 'SSP',
        'DJ': 'DJF',
        'ER': 'ERN',
        'SO': 'SOS',
        'ET': 'ETB',
        'ZW': 'ZWL',
        'NA': 'NAD',
        'BW': 'BWP',
        'ZM': 'ZMW',
        'MW': 'MWK',
        'MZ': 'MZN',
        'MG': 'MGA',
        'TZ': 'TZS',
        'UG': 'UGX',
        'RW': 'RWF',
        'BI': 'BIF',
        'BD': 'BHD',
        'OM': 'OMR',
        'QA': 'QAR',
        'YE': 'YER',
        'SD': 'SDG',
        'SS': 'SSP',
        'DJ': 'DJF',
        'ER': 'ERN',
        'SO': 'SOS',
        'ET': 'ETB',
        'ZW': 'ZWL',
        'NA': 'NAD',
        'BW': 'BWP',
        'ZM': 'ZMW',
        'MW': 'MWK',
        'MZ': 'MZN',
        'MG': 'MGA',
        'TZ': 'TZS',
        'UG': 'UGX',
        'RW': 'RWF',
        'BI': 'BIF',
        'CM': 'XAF',
        'CG': 'XAF',
        'CF': 'XAF',
        'TD': 'XAF',
        'LY': 'LYD',
        'TN': 'TND',
        'DZ': 'DZD',
        'MA': 'MAD',
        'MO': 'MOP',
        'LA': 'LAK',
        'MY': 'MYR',
        'SG': 'SGD',
        'PH': 'PHP',
        'ID': 'IDR',
        'VN': 'VND',
        'TH': 'THB',
        'KH': 'KHR',
        'MM': 'MMK',
        'BN': 'BND',
        'IN': 'INR',
        'NP': 'NPR',
        'BD': 'BDT',
        'PK': 'PKR',
        'AF': 'AFN',
        'TJ': 'TJS',
        'UZ': 'UZS',
        'KG': 'KGS',
        'TM': 'TMT',
        'AZ': 'AZN',
        'GE': 'GEL',
        'AM': 'AMD',
        'SY': 'SYP',
        'IQ': 'IQD',
        'IR': 'IRR',
        'KW': 'KWD',
        'BH': 'BHD',
        'OM': 'OMR',
        'QA': 'QAR',
        'YE': 'YER',
        'SD': 'SDG',
        'SS': 'SSP',
        'DJ': 'DJF',
        'ER': 'ERN',
        'SO': 'SOS',
        'ET': 'ETB',
        'ZW': 'ZWL',
        'NA': 'NAD',
        'BW': 'BWP',
        'ZM': 'ZMW',
        'MW': 'MWK',
        'MZ': 'MZN',
        'MG': 'MGA',
        'TZ': 'TZS',
        'UG': 'UGX',
        'RW': 'RWF',
        'BI': 'BIF',

    }
    
    return country_currency_map.get(country_code, 'USD')
