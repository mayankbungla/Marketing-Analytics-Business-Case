-- Query to clean and normalize the data
-- Extracting views and clicks from viewsclickscombined column,

select * from dbo.engagement_data;

Select EngagementId,
	ContentID,
	CampaignID,
	ProductId,
	Likes,
	UPPER (replace(ContentType, 'Socialmedia','Social media')) as contentType,

	--EXTRACT VIEWS: Finds the hyphen position and grabs all characters to the left of it.Example: '150-40' becomes '150'
    LEFT ( ViewsClicksCombined, CHARINDEX ('-', ViewsClicksCombined)-1) as views, 

	-- EXTRACT CLICKS: Finds the hyphen position. Total length of the string minus the position of the hyphen gives the number of characters to the right of the hyphen.
	Right ( ViewsClicksCombined, Len(viewsclickscombined)- CHARINDEX ('-',ViewsClicksCombined)) as clicks,

	format(convert(date, engagementdate), 'dd.MM.yyyy') as engagementDate

from dbo.engagement_data
where ContentType != 'newsletter'; -- Not relevant for our analysis
