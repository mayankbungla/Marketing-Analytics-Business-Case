-- Query to clean and normalize the data
-- Extracting views and clicks from viewsclickscombined column,

select * from dbo.engagement_data

Select EngagementId,
	ContentID,
	CampaignID,
	ProductId,
	Likes,
	UPPER (replace(ContentType, 'Socialmedia','Social media')) as contentType,
	LEFT ( ViewsClicksCombined, CHARINDEX ('-', ViewsClicksCombined)-1) as views,
	Right ( ViewsClicksCombined, Len(viewsclickscombined)- CHARINDEX ('-',ViewsClicksCombined)) as clicks,
	format(convert(date, engagementdate), 'dd.MM.yyyy') as engagementDate

from dbo.engagement_data
where ContentType != 'newsletter'; -- Not relevant for our analysis