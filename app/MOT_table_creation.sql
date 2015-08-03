--TESTRESULT
CREATE TABLE TESTRESULT (
  TESTID INT 
  ,VEHICLEID INT 
  ,TESTDATE DATE
  ,TESTCLASSID VARCHAR2(2)
  ,TESTTYPE VARCHAR2(2)
  ,TESTRESULT VARCHAR2(3)
  ,TESTMILEAGE INT 
  ,POSTCODEREGION VARCHAR2(2)
  ,MAKE VARCHAR2(30)
  ,MODEL VARCHAR2(30)
  ,COLOUR VARCHAR2(16)
  ,FUELTYPE VARCHAR2(1)
  ,CYLCPCTY INT 
  ,FIRSTUSEDATE DATE
  ,PRIMARY KEY (TESTID)
  ,constraint test_id_nonzero check (TESTID > 0)
  ,constraint vehicle_id_nonzero check (VEHICLEID > 0)
  ,constraint testmileage_nonzero check (TESTMILEAGE > 0)
  ,constraint cyclecapacity_nonzero check (CYLCPCTY > 0)
  )
;

--TESTRESULT used columns only

SELECT * FROM TESTRESULT;
DROP TABLE TESTRESULT PURGE;
CREATE TABLE TESTRESULT (
  TESTID INT  
  ,TESTCLASSID VARCHAR2(2)
  ,TESTTYPE VARCHAR2(2)
  ,TESTRESULT VARCHAR2(3)  
  ,MAKE VARCHAR2(30)
  ,MODEL VARCHAR2(30)  
  ,FIRSTUSEDATE DATE
  ,PRIMARY KEY (TESTID)
  ,constraint test_id_nonzero check (TESTID > 0) 
  )
;

CREATE INDEX IDX1 ON  TESTRESULT(TESTTYPE, TESTRESULT, TESTCLASSID)
;

delete from testresult where make = 'UNCLASSIFIED';
delete from testresult where testclassid <> 4;
delete from testresult where TESTRESULT not in ('P', 'F');

---load test result data into this table-----

--general table creation and process
 SELECT * FROM TESTRESULT
 
 select testtype, count(1)
 from testresult group by testtype

--TESTITEM
CREATE TABLE TESTITEM (
	TESTID INT
	,RFRID SMALLINT
	,RFRTYPE VARCHAR2(1)
	,LATLOCATIONID VARCHAR2(1)
	,LONGLOCATIONID VARCHAR2(1)
	,VERTLOCATIONID VARCHAR2(1)
	,DMARK VARCHAR2(1)
	,constraint test_id_nonzero1 check (TESTID > 0)
  ,constraint rfr_id_nonzero1 check (RFRID > 0)
	)
;

CREATE INDEX IDX2 ON  TESTITEM(TESTID)
;

CREATE INDEX IDX3 ON  TESTITEM(RFRID)
;
-----load test item data into this table-------

--TESTITEM_DETAIL
CREATE TABLE TESTITEM_DETAIL (
	RFRID SMALLINT
	,TESTCLASSID VARCHAR2(2)
	,TSTITMID SMALLINT
	,MINORITEM VARCHAR2(1)
	,RFRDESC VARCHAR2(250)
	,RFRLOCMARKER VARCHAR2(1)
	,RFRINSPMANDESC VARCHAR2(500)
	,RFRADVISORYTEXT VARCHAR2(250)
	,TSTITMSETSECID SMALLINT
	,PRIMARY KEY (RFRID, TESTCLASSID)
	,constraint rfr_id_nonzero check (RFRID > 0)
  ,constraint tstitmid_id_nonzero check (TSTITMID > 0)
  ,constraint tstitmsetsecid_id_nonzero check (TSTITMSETSECID > 0)
	)
;

CREATE INDEX IDX4 ON  TESTITEM_DETAIL(TSTITMID, TESTCLASSID)
;

CREATE INDEX IDX5 ON  TESTITEM_DETAIL(TSTITMSETSECID, TESTCLASSID)
;

-----load test item detail data into this table-------

--TESTITEM_GROUP
CREATE TABLE TESTITEM_GROUP (
	TSTITMID SMALLINT 
  ,TESTCLASSID VARCHAR2(2)
	,PARENTID SMALLINT
	,TSTITMSETSECID SMALLINT
	,ITEMNAME VARCHAR2(100)
	,PRIMARY KEY (TSTITMID, TESTCLASSID)
  ,constraint tstitmid_id_nonzero1 check (TSTITMID > 0)
  ,constraint parent_id_nonzero check (PARENTID > 0)
  ,constraint tstitmsetsecid_id_nonzero1 check (TSTITMSETSECID > 0)
  )
  ;
  
CREATE INDEX IDX6 ON TESTITEM_GROUP (PARENTID, TESTCLASSID);
CREATE INDEX IDX7 ON TESTITEM_GROUP(TSTITMSETSECID, TESTCLASSID);

-----load test item group data into this table-------


-- creation of failreasons view to form levels of fault from parent-child relationships --
drop view failreasons ;

create view failreasons as
SELECT distinct a.RFRID
  ,a.RFRDESC
  ,b.ITEMNAME AS LEVEL1
  ,c.ITEMNAME AS LEVEL2
  ,d.ITEMNAME AS LEVEL3
  ,e.ITEMNAME AS LEVEL4
  ,f.ITEMNAME AS LEVEL5  
FROM TESTITEM_DETAIL a
  INNER JOIN TESTITEM_GROUP b
    ON a.TSTITMID = b.TSTITMID
    AND a.TESTCLASSID = b.TESTCLASSID
  LEFT JOIN TESTITEM_GROUP c
    ON b.PARENTID = c.TSTITMID
    AND b.TESTCLASSID = c.TESTCLASSID
  LEFT JOIN TESTITEM_GROUP d
    ON c.PARENTID = d.TSTITMID
    AND c.TESTCLASSID = d.TESTCLASSID
  LEFT JOIN TESTITEM_GROUP e
    ON d.PARENTID = e.TSTITMID
    AND d.TESTCLASSID = e.TESTCLASSID
  LEFT JOIN TESTITEM_GROUP f
    ON e.PARENTID = f.TSTITMID
    AND e.TESTCLASSID = f.TESTCLASSID
    ORDER BY 1


create or replace VIEW RFRIDVIEW AS select /*+parallel*/ distinct a.rfrid, c.testid, TRIM(a.level2) SHORTDESC, 
TRIM(a.level1) MEDIUMDESC, TRIM(a.rfrdesc) LONGDESC 
from failreasons a right join testitem c
on a.rfrid = c.RFRID

create table RFRIDTABLE AS select /*+parallel*/ * from rfridview
    
    
--view is focused on make and model, so columns like vehicleid, testclassid, testdate removed

-- change model name to just the first letter from the former model name

create or REPLACE VIEW MOT2013VIEW AS select /*+parallel*/ distinct a.*, TRIM(b.make) MAKE, regexp_substr(TRIM(b.model), '\w+') MODEL, TRIM(b.testresult) TESTRESULT, extract(year from b.firstusedate) FIRSTYEARONROAD
from RFRIDTABLE a right join testresult b
on a.testid = b.TESTID
where make <> 'UNCLASSIFIED'
--AND TESTRESULT = 'F'
--AND TESTTYPE = 'N'
and b.TESTCLASSID = '4'
--order by b.testid;

select * from testresult

select /*+parallel*/ * from mot2013view;

select /*+parallel*/ * from mot2013view WHERE ROWNUM < 10;

drop table MOT2013 purge;
---------------create table to hold the entire 2013 test data---------------------------------------
create table MOT2013 as select /*+parallel(24)*/ * from mot2013view --where rownum < 1000001;

select * from MOT2013;


select * from testitem;

select * from testresult;

create index idx10 on mot2013(make);

select count(1) from MOT2013; -- 11087395 for first 10 million test result records

select count(1) from testresult;

select count(distinct testid) from MOT2013;--4836568

select count(distinct rfrid) from MOT2013;--1547

-- change model name to just the first letter from the former model name
--update /*+parallel(4) nologging*/ MOT2013 set model = regexp_substr(model,'\w+');

drop table MOT2013FAULTSUMMARY purge;
----------------summarise data to find out the number of cars with particular faults by make and model---------------
create table MOT2013FAULTSUMMARY AS 
select /*+parallel*/ MAKE, MODEL, FIRSTYEARONROAD, TESTRESULT, SHORTDESC, mediumdesc, longdesc, count(model) CATEGORYSUM 
from MOT2013 
where 
group by make, model, FIRSTYEARONROAD, TESTRESULT, SHORTDESC, mediumdesc, longdesc
--order by make, model, FIRSTYEARONROAD, TESTRESULT;

select count(1) from MOT2013FAULTSUMMARY where shortdesc is null; --1161401 ; 1206779

select * from MOT2013FAULTSUMMARY where model is null;

delete from MOT2013FAULTSUMMARY where shortdesc is null;
delete from MOT2013FAULTSUMMARY where testresult not in ('P', 'F');
                       
select length(make) from MOT2013FAULTSUMMARY;


drop table MOT2013FAULTSUMMARYLEVEL1 purge;
--focus on the short description---------
create table MOT2013FAULTSUMMARYLEVEL1 as
select /*+parallel*/ MAKE, MODEL, SHORTDESC, TESTRESULT, sum(CATEGORYSUM) CATEGORYSUM from
MOT2013FAULTSUMMARY group by make, model, SHORTDESC, TESTRESULT
order by make, model, categorysum;

SELECT * FROM MOT2013FAULTSUMMARYLEVEL1;

select count(1) from MOT2013FAULTSUMMARYLEVEL1; --155039

--select * from MOT2013FAULTSUMMARYSUMMED where make like '%FORD%';

---------------------------------- other sample computations --------------------------------------------------------------------------

---Initial, Completed Test Volumes by Class 2013 (As calculated in VOSA effectiveness report)
SELECT TESTCLASSID
	,TESTRESULT
	,COUNT(*) AS TEST_VOLUME
FROM TESTRESULT
WHERE TESTTYPE='N'
	AND TESTRESULT IN('P','F','PRS')
  --AND TESTDATE BETWEEN '2009-04-01' AND '2010-03-31'
  AND trunc(TESTDATE) BETWEEN '01-Jan-2013' AND '31-Mar-2013'
GROUP BY TESTCLASSID
	,TESTRESULT
;

---RfR Volumes and Distinct Test Failures 2008 for Class 7 Vehicles by Top Level Test Item Group (For vehicles as presented for initial test)
SELECT d.ITEMNAME
	,COUNT(*) AS RFR_VOLUME
	,COUNT(DISTINCT a.TESTID) AS TEST_VOLUME
FROM TESTRESULT a
	INNER JOIN TESTITEM b
		ON a.TESTID=b.TESTID
	INNER JOIN TESTITEM_DETAIL c
		ON b.RFRID=c.RFRID
		AND a.TESTCLASSID = c.TESTCLASSID
	INNER JOIN TESTITEM_GROUP d
		ON c.TSTITMSETSECID = d.TSTITMID
		AND c.TESTCLASSID = d.TESTCLASSID
WHERE a.TESTDATE BETWEEN '01-Jan-2008' AND '31-Dec-2013'
	AND a.TESTCLASSID = '7'
	AND a.TESTTYPE='N'
	AND a.TESTRESULT IN('F','PRS')
	AND b.RFRTYPE IN('F','P')
GROUP BY d.ITEMNAME
;

-----Basic Expansion of RfR Hierarchy for Class 5 Vehicles
SELECT a.RFRID
	,a.RFRDESC
	,b.ITEMNAME AS LEVEL1
	,c.ITEMNAME AS LEVEL2
	,d.ITEMNAME AS LEVEL3
	,e.ITEMNAME AS LEVEL4
	,f.ITEMNAME AS LEVEL5
FROM TESTITEM_DETAIL a
	INNER JOIN TESTITEM_GROUP b
		ON a.TSTITMID = b.TSTITMID
		AND a.TESTCLASSID = b.TESTCLASSID
	LEFT JOIN TESTITEM_GROUP c
		ON b.PARENTID = c.TSTITMID
		AND b.TESTCLASSID = c.TESTCLASSID
	LEFT JOIN TESTITEM_GROUP d
		ON c.PARENTID = d.TSTITMID
		AND c.TESTCLASSID = d.TESTCLASSID
	LEFT JOIN TESTITEM_GROUP e
		ON d.PARENTID = e.TSTITMID
		AND d.TESTCLASSID = e.TESTCLASSID
	LEFT JOIN TESTITEM_GROUP f
		ON e.PARENTID = f.TSTITMID
		AND e.TESTCLASSID = f.TESTCLASSID
WHERE a.TESTCLASSID = '5'
;

select count(testid) from testresult -- 37390457

select count(distinct testid) from testresult -- 37390457

select count(distinct vehicleid) from testresult -- 27823579 This shows the count of cars that came for testing more than once in 2013




SELECT  FILE_NAME, BLOCKS, TABLESPACE_NAME
FROM DBA_DATA_FILES;


