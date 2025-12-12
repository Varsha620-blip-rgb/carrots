from database.db import execute_query, fetch_query, fetch_one
from datetime import datetime, date

class GoldRateService:
    PURITIES = ['24K', '22K', '21K', '18K', '14K', '916', '875', '750', '585']
    
    @staticmethod
    def get_current_rate(purity='22K'):
        result = fetch_one("""
            SELECT rate_per_gram, making_charges, rate_date
            FROM gold_rates
            WHERE purity = ? AND is_active = 1
            ORDER BY rate_date DESC
            LIMIT 1
        """, (purity,))
        
        if result:
            return {
                'rate_per_gram': result[0],
                'making_charges': result[1],
                'rate_date': result[2]
            }
        return None
    
    @staticmethod
    def get_all_current_rates():
        rates = fetch_query("""
            SELECT gr1.purity, gr1.rate_per_gram, gr1.making_charges, gr1.rate_date
            FROM gold_rates gr1
            INNER JOIN (
                SELECT purity, MAX(rate_date) as max_date
                FROM gold_rates
                WHERE is_active = 1
                GROUP BY purity
            ) gr2 ON gr1.purity = gr2.purity AND gr1.rate_date = gr2.max_date
            WHERE gr1.is_active = 1
            ORDER BY gr1.purity
        """)
        
        return [{'purity': r[0], 'rate_per_gram': r[1], 'making_charges': r[2], 'rate_date': r[3]} for r in rates]
    
    @staticmethod
    def update_rate(purity, rate_per_gram, making_charges=0, notes="", rate_date=None):
        if rate_date is None:
            rate_date = date.today()
        
        existing = fetch_one("""
            SELECT id FROM gold_rates 
            WHERE rate_date = ? AND purity = ?
        """, (rate_date, purity))
        
        if existing:
            execute_query("""
                UPDATE gold_rates 
                SET rate_per_gram = ?, making_charges = ?, notes = ?, date_modified = ?
                WHERE rate_date = ? AND purity = ?
            """, (rate_per_gram, making_charges, notes, datetime.now(), rate_date, purity))
        else:
            execute_query("""
                INSERT INTO gold_rates (rate_date, purity, rate_per_gram, making_charges, notes, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (rate_date, purity, rate_per_gram, making_charges, notes, datetime.now(), datetime.now()))
        
        return True
    
    @staticmethod
    def get_rate_history(purity=None, limit=30):
        if purity:
            return fetch_query("""
                SELECT id, rate_date, purity, rate_per_gram, making_charges, notes
                FROM gold_rates
                WHERE purity = ? AND is_active = 1
                ORDER BY rate_date DESC
                LIMIT ?
            """, (purity, limit))
        else:
            return fetch_query("""
                SELECT id, rate_date, purity, rate_per_gram, making_charges, notes
                FROM gold_rates
                WHERE is_active = 1
                ORDER BY rate_date DESC, purity
                LIMIT ?
            """, (limit,))
    
    @staticmethod
    def delete_rate(rate_id):
        execute_query("""
            UPDATE gold_rates SET is_active = 0, date_modified = ?
            WHERE id = ?
        """, (datetime.now(), rate_id))
        return True
    
    @staticmethod
    def calculate_item_value(weight_gm, purity='22K', include_making=True):
        rate_info = GoldRateService.get_current_rate(purity)
        if not rate_info:
            return None
        
        base_value = weight_gm * rate_info['rate_per_gram']
        if include_making:
            making = weight_gm * rate_info['making_charges']
            return base_value + making
        return base_value


class DiamondRateService:
    CLARITIES = ['FL', 'IF', 'VVS1', 'VVS2', 'VS1', 'VS2', 'SI1', 'SI2', 'I1', 'I2', 'I3']
    COLORS = ['D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M']
    CUTS = ['Excellent', 'Very Good', 'Good', 'Fair', 'Poor']
    SHAPES = ['Round', 'Princess', 'Cushion', 'Oval', 'Emerald', 'Pear', 'Marquise', 'Radiant', 'Heart', 'Asscher']
    
    @staticmethod
    def update_rate(clarity, color, rate_per_carat, carat_from=0, carat_to=10, 
                   shape='Round', certification=None, notes="", rate_date=None):
        if rate_date is None:
            rate_date = date.today()
        
        existing = fetch_one("""
            SELECT id FROM diamond_rates 
            WHERE clarity = ? AND color = ? AND shape = ? AND rate_date = ?
        """, (clarity, color, shape, rate_date))
        
        if existing:
            execute_query("""
                UPDATE diamond_rates 
                SET rate_per_carat = ?, carat_from = ?, carat_to = ?, certification = ?, 
                    notes = ?, is_active = 1, date_modified = ?
                WHERE id = ?
            """, (rate_per_carat, carat_from, carat_to, certification, notes, datetime.now(), existing[0]))
        else:
            execute_query("""
                INSERT INTO diamond_rates (rate_date, shape, clarity, color, carat_from, carat_to, 
                                          rate_per_carat, certification, notes, date_created, date_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (rate_date, shape, clarity, color, carat_from, carat_to, 
                  rate_per_carat, certification, notes, datetime.now(), datetime.now()))
        return True
    
    @staticmethod
    def get_current_rate(clarity='VS1', color='G', shape='Round'):
        result = fetch_one("""
            SELECT id, rate_date, shape, clarity, color, carat_from, carat_to, 
                   rate_per_carat, certification, notes
            FROM diamond_rates
            WHERE clarity = ? AND color = ? AND shape = ? AND is_active = 1
            ORDER BY rate_date DESC
            LIMIT 1
        """, (clarity, color, shape))
        
        if result:
            return {
                'id': result[0],
                'rate_date': result[1],
                'shape': result[2],
                'clarity': result[3],
                'color': result[4],
                'carat_from': result[5],
                'carat_to': result[6],
                'rate_per_carat': result[7],
                'certification': result[8],
                'notes': result[9]
            }
        return None
    
    @staticmethod
    def get_all_current_rates():
        return fetch_query("""
            SELECT DISTINCT clarity, color, shape, rate_per_carat
            FROM diamond_rates
            WHERE is_active = 1
            ORDER BY clarity, color
        """)
    
    @staticmethod
    def get_rate_history(limit=50):
        return fetch_query("""
            SELECT id, rate_date, shape, clarity, color, carat_from, carat_to, 
                   rate_per_carat, certification, notes
            FROM diamond_rates
            WHERE is_active = 1
            ORDER BY rate_date DESC, id DESC
            LIMIT ?
        """, (limit,))
    
    @staticmethod
    def calculate_diamond_value(carat, clarity='VS1', color='G', shape='Round'):
        rate = DiamondRateService.get_current_rate(clarity, color, shape)
        if rate:
            return carat * rate['rate_per_carat']
        return 0
    
    @staticmethod
    def delete_rate(rate_id):
        execute_query("""
            UPDATE diamond_rates SET is_active = 0, date_modified = ?
            WHERE id = ?
        """, (datetime.now(), rate_id))
        return True
