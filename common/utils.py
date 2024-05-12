from .enums import RatingTag

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