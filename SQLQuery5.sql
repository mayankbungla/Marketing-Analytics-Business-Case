Select * from customer_journey
where JourneyID = 23
													-- CTE to identify and tag duplicate records

With duplicate_record As (
Select JourneyId,
	customerId,
	ProductID,
	VisitDate,
	Stage,
	Action,
	Duration,
														--- Using windows function to identify duplicates
	ROW_NUMBER() over (
	Partition by customerId,ProductID,visitdate, stage, action
	order by JourneyID) as row_num
from dbo.customer_journey)

								-- Select all rows from CTE where row_num >1, which indicate duplicate entries
Select * from duplicate_record
where row_num>1
order by journeyid

--*****************************************************************************************

															-- Outer query to select final cleaned and standardized data

Select JourneyId,customerId,ProductID,VisitDate,Stage,Action,
	coalesce(duration, avg_duration) as duration
	from
(										-- subquery to process and clean data
Select JourneyId,
	customerId,
	ProductID,
	VisitDate,
	Upper(Stage) as Stage,
	Action,
	Duration,
	avg(duration) over(partition by visitdate) as avg_duration,
	ROW_NUMBER() over( partition by customerId,ProductID,VisitDate, Upper(Stage),Action order by Journeyid) as row_num		
from dbo.customer_journey) as subquery
where row_num = 1
order by JourneyID
