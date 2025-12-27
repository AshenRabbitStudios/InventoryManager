import logging
from datetime import datetime, timedelta
from models import Sale, Product

logger = logging.getLogger(__name__)

class PredictionService:
    """
    Service for predicting future inventory needs based on historical sales data.
    """
    
    @staticmethod
    def predict_sales_next_30_days(product_id):
        """
        Predicts the number of sales for a specific product in the next 30 days
        using a simple moving average of the last 90 days.
        """
        try:
            ninety_days_ago = datetime.now() - timedelta(days=90)
            recent_sales = Sale.select().where(
                (Sale.product == product_id) & 
                (Sale.date >= ninety_days_ago)
            ).count()
            
            # Simple average: sales in 90 days / 3 = predicted sales in 30 days
            prediction = round(recent_sales / 3.0, 2)
            logger.info(f"Predicted {prediction} sales for product {product_id} in next 30 days.")
            return prediction
        except Exception as e:
            logger.error(f"Error predicting sales for product {product_id}: {e}", exc_info=True)
            return 0.0

    @staticmethod
    def get_low_stock_alerts(threshold=2):
        """
        Returns products that have inventory below the threshold.
        """
        try:
            low_stock_products = Product.select().where(Product.inventory_count <= threshold)
            return list(low_stock_products)
        except Exception as e:
            logger.error(f"Error fetching low stock alerts with threshold {threshold}: {e}", exc_info=True)
            return []
