-- Categorizing the products based on their price

select productID, ProductName, Price,		
Case										
	when price<50 then 'Low'
	when price between 50 and 200 then 'Medium'
	when price>200 then 'High'
End as PriceCategory		-- Labeling products based on their price
from dbo.products;
