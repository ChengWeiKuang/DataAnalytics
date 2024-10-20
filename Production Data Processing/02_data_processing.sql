-- For each SerialNum, get the Week where it was first tested, and store into a temp table. 
IF OBJECT_ID('tempdb..#loadweek') IS NOT NULL DROP TABLE #loadweek; 
WITH sn_first_ts AS (
	SELECT SerialNum, 
		MIN(TestTimeStamp) AS FirstTestTimeStamp
	FROM dbo.generated_raw_data AS a 
	GROUP BY SerialNum
)
SELECT a.SerialNum, b.Week AS LoadWeek
INTO #loadweek
FROM sn_first_ts AS a 
	INNER JOIN dbo.Calendar AS b 
		ON a.FirstTestTimeStamp BETWEEN b.StartDate AND b.EndDate
;

-- Create a temp rawdata table with all information, plus module LoadWeek and indicators for first & last test. 
IF OBJECT_ID('tempdb..#rawdata') IS NOT NULL DROP TABLE #rawdata
SELECT b.LoadWeek, 
	a.SerialNum, a.ProductName, a.TestName, a.MachineID, a.TestResult, a.TestDuration_s, 
	RANK() OVER (PARTITION BY a.SerialNum, a.TestName ORDER BY TestTimeStamp) AS TestCount_Asc, 
	RANK() OVER (PARTITION BY a.SerialNum, a.TestName ORDER BY TestTimeStamp DESC) AS TestCount_Desc
INTO #rawdata
FROM dbo.generated_raw_data AS a
	INNER JOIN #loadweek AS b 
		ON a.SerialNum = b.SerialNum

-- Create a summary table for machine performances. 
TRUNCATE TABLE dbo.summary_machine
INSERT INTO dbo.summary_machine
SELECT LoadWeek, ProductName, TestName, MachineID, 
	COUNT(SerialNum) AS TestCount, 
	SUM(CASE WHEN TestResult = 'PASS' THEN 1 ELSE 0 END)*1.0000/COUNT(SerialNum) AS PassingRate, 
	AVG(CASE WHEN TestResult = 'PASS' THEN TestDuration_s END) AS AvgTestDuration_Pass_s,
	AVG(CASE WHEN TestResult != 'PASS' THEN TestDuration_s END) AS AvgTestDuration_Fail_s
FROM #rawdata
GROUP BY LoadWeek, ProductName, TestName, MachineID

-- Create a summary table for test yields, qty & durations, at Product-Test Level. 
TRUNCATE TABLE dbo.summary_prod_test
INSERT INTO dbo.summary_prod_test
SELECT LoadWeek, ProductName, TestName, 
	COUNT(DISTINCT SerialNum) AS LoadQty, 
	COUNT(DISTINCT CASE WHEN (TestCount_Asc = 1 AND TestResult = 'PASS') THEN SerialNum END)*1.0000/COUNT(DISTINCT SerialNum) AS FirstPassYield, 
	COUNT(DISTINCT CASE WHEN (TestCount_Desc = 1 AND TestResult = 'PASS') THEN SerialNum END)*1.0000/COUNT(DISTINCT SerialNum) AS CummYield, 
	AVG(CASE WHEN TestResult = 'PASS' THEN TestDuration_s END) AS AvgTestDuration_Pass_s,
	AVG(CASE WHEN TestResult != 'PASS' THEN TestDuration_s END) AS AvgTestDuration_Fail_s
FROM #rawdata 
GROUP BY LoadWeek, ProductName, TestName

-- Create another summary table at Product Level generally. 
TRUNCATE TABLE dbo.summary_prod
INSERT INTO dbo.summary_prod
SELECT LoadWeek, ProductName, 
	EXP(SUM(LOG(FirstPassYield))) AS FirstPassYield,
	EXP(SUM(LOG(CummYield))) AS CummYield,
	MIN(LoadQty) AS LoadQty
FROM dbo.summary_prod_test
GROUP BY LoadWeek, ProductName

/* 
SELECT * FROM dbo.summary_machine
SELECT * FROM dbo.summary_prod_test
SELECT * FROM dbo.summary_prod
*/ 
