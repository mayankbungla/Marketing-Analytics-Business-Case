
-- Replacing Double spaces from ReviewText column in Customer_Reviews table


select ReviewID,
	CustomerID,
	ProductID,
	ReviewDate,
	Rating,
	Replace (ReviewText, '  ',' ') as ReviewText
from dbo.customer_reviews;
