Select * from customers
select * from geography

-- Merging the tables customers and geography table to enrich customer data with geographic information

Select c.customerid, c.CustomerName, c.email, c.gender, c.age,
	 g.country, g.city
	from customers as c
	left join
	geography as g
	on c.GeographyID = g.GeographyID;
