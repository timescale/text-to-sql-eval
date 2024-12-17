CREATE TABLE public.border_info (
    state_name text,
    border text
);

COMMENT ON COLUMN public.border_info.state_name IS 'The name of the state that shares a border with another state or country.';

COMMENT ON COLUMN public.border_info.border IS 'The name of the state that shares a border with the state specified in the state_name column.';

CREATE TABLE public.city (
    city_name text,
    population bigint,
    country_name text DEFAULT ''::text NOT NULL,
    state_name text
);

COMMENT ON COLUMN public.city.city_name IS 'The name of the city';

COMMENT ON COLUMN public.city.population IS 'The population of the city';

COMMENT ON COLUMN public.city.country_name IS 'The name of the country where the city is located';

COMMENT ON COLUMN public.city.state_name IS 'The name of the state where the city is located';

CREATE TABLE public.highlow (
    state_name text,
    highest_elevation text,
    lowest_point text,
    highest_point text,
    lowest_elevation text
);

COMMENT ON COLUMN public.highlow.state_name IS 'The name of the state';

COMMENT ON COLUMN public.highlow.highest_elevation IS 'The highest elevation point in the state in meters above sea level';

COMMENT ON COLUMN public.highlow.lowest_point IS 'The lowest elevation point in the state';

COMMENT ON COLUMN public.highlow.highest_point IS 'The highest point in the state. If unknown, use ''Unnamed location''.';

COMMENT ON COLUMN public.highlow.lowest_elevation IS 'The lowest point in the state in meters above sea level';

CREATE TABLE public.lake (
    lake_name text,
    area double precision,
    country_name text DEFAULT ''::text NOT NULL,
    state_name text
);

COMMENT ON COLUMN public.lake.lake_name IS 'The name of the lake';

COMMENT ON COLUMN public.lake.area IS 'The area of the lake in square kilometers';

COMMENT ON COLUMN public.lake.country_name IS 'The name of the country where the lake is located';

COMMENT ON COLUMN public.lake.state_name IS 'The name of the state where the lake is located (if applicable)';

CREATE TABLE public.mountain (
    mountain_name text,
    mountain_altitude bigint,
    country_name text DEFAULT ''::text NOT NULL,
    state_name text
);

COMMENT ON COLUMN public.mountain.mountain_name IS 'The name of the mountain';

COMMENT ON COLUMN public.mountain.mountain_altitude IS 'The altitude of the mountain in meters';

COMMENT ON COLUMN public.mountain.country_name IS 'The name of the country where the mountain is located';

COMMENT ON COLUMN public.mountain.state_name IS 'The name of the state or province where the mountain is located (if applicable)';

CREATE TABLE public.river (
    river_name text,
    length bigint,
    country_name text DEFAULT ''::text NOT NULL,
    traverse text
);

COMMENT ON COLUMN public.river.river_name IS 'The name of the river. Names exclude the word ''river'' e.g. ''Mississippi'' instead of ''Mississippi River''';

COMMENT ON COLUMN public.river.length IS 'The length of the river in meters';

COMMENT ON COLUMN public.river.country_name IS 'The name of the country the river flows through';

COMMENT ON COLUMN public.river.traverse IS 'The cities or landmarks the river passes through. Comma delimited and in title case, eg `New York,Albany,Boston`';

CREATE TABLE public.state (
    state_name text,
    population bigint,
    area double precision,
    country_name text DEFAULT ''::text NOT NULL,
    capital text,
    density double precision
);

COMMENT ON COLUMN public.state.state_name IS 'The name of the state';

COMMENT ON COLUMN public.state.population IS 'The population of the state';

COMMENT ON COLUMN public.state.area IS 'The area of the state in square kilometers';

COMMENT ON COLUMN public.state.country_name IS 'The name of the country the state belongs to';

COMMENT ON COLUMN public.state.capital IS 'The name of the capital city of the state';

COMMENT ON COLUMN public.state.density IS 'The population density of the state in people per square kilometer';

INSERT INTO public.border_info VALUES ('California', 'Nevada');
INSERT INTO public.border_info VALUES ('California', 'Arizona');
INSERT INTO public.border_info VALUES ('California', 'Oregon');
INSERT INTO public.border_info VALUES ('Texas', 'Louisiana');
INSERT INTO public.border_info VALUES ('Texas', 'Oklahoma');
INSERT INTO public.border_info VALUES ('Texas', 'New Mexico');
INSERT INTO public.border_info VALUES ('Florida', 'Alabama');
INSERT INTO public.border_info VALUES ('Florida', 'Georgia');
INSERT INTO public.border_info VALUES ('Florida', 'Atlantic Ocean');
INSERT INTO public.border_info VALUES ('New York', 'Pennsylvania');
INSERT INTO public.border_info VALUES ('New York', 'Connecticut');
INSERT INTO public.border_info VALUES ('New York', 'Massachusetts');

INSERT INTO public.city VALUES ('New York', 1000000, 'United States', 'New York');
INSERT INTO public.city VALUES ('Los Angeles', 5000000, 'United States', 'California');
INSERT INTO public.city VALUES ('Chicago', 1500000, 'United States', 'Illinois');
INSERT INTO public.city VALUES ('Houston', 2000000, 'United States', 'Texas');
INSERT INTO public.city VALUES ('Toronto', 800000, 'Canada', 'Ontario');
INSERT INTO public.city VALUES ('Mexico City', 600000, 'Mexico', 'Distrito Federal');
INSERT INTO public.city VALUES ('Sao Paulo', 3000000, 'Brazil', 'Sao Paulo');
INSERT INTO public.city VALUES ('Mumbai', 1200000, 'India', 'Maharashtra');
INSERT INTO public.city VALUES ('London', 900000, 'United Kingdom', 'England');
INSERT INTO public.city VALUES ('Tokyo', 700000, 'Japan', 'Tokyo');

INSERT INTO public.highlow VALUES ('California', '4421', 'Death Valley', 'Mount Whitney', '-86');
INSERT INTO public.highlow VALUES ('Texas', '2667', 'Gulf of Mexico', 'Guadalupe Peak', '0');
INSERT INTO public.highlow VALUES ('Florida', NULL, 'Atlantic Ocean', 'Unnamed location', '0');
INSERT INTO public.highlow VALUES ('New York', '1629', 'Atlantic Ocean', 'Mount Marcy', '0');
INSERT INTO public.highlow VALUES ('Ontario', NULL, 'Atlantic Ocean', 'Unnamed location', '0');
INSERT INTO public.highlow VALUES ('Sao Paulo', NULL, 'Atlantic Ocean', 'Unnamed location', '0');
INSERT INTO public.highlow VALUES ('Guangdong', NULL, 'South China Sea', 'Unnamed location', '0');
INSERT INTO public.highlow VALUES ('Maharashtra', NULL, 'Arabian Sea', 'Unnamed location', '0');
INSERT INTO public.highlow VALUES ('England', '978', 'North Sea', 'Scafell Pike', '0');
INSERT INTO public.highlow VALUES ('Tokyo', '3776', 'Pacific Ocean', 'Mount Fuji', '0');

INSERT INTO public.lake VALUES ('Lake Superior', 1000, 'United States', 'Michigan');
INSERT INTO public.lake VALUES ('Lake Michigan', 500, 'United States', 'Michigan');
INSERT INTO public.lake VALUES ('Lake Huron', 300, 'United States', 'Michigan');
INSERT INTO public.lake VALUES ('Lake Erie', 200, 'United States', 'Ohio');
INSERT INTO public.lake VALUES ('Lake Ontario', 400, 'United States', 'New York');
INSERT INTO public.lake VALUES ('Lake Victoria', 800, 'Tanzania', NULL);
INSERT INTO public.lake VALUES ('Lake Tanganyika', 600, 'Tanzania', NULL);
INSERT INTO public.lake VALUES ('Lake Malawi', 700, 'Tanzania', NULL);
INSERT INTO public.lake VALUES ('Lake Baikal', 900, 'Russia', NULL);
INSERT INTO public.lake VALUES ('Lake Qinghai', 1200, 'China', NULL);

INSERT INTO public.mountain VALUES ('Mount Everest', 10000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('K2', 5000, 'Pakistan', NULL);
INSERT INTO public.mountain VALUES ('Kangchenjunga', 3000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('Lhotse', 2000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('Makalu', 4000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('Cho Oyu', 8000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('Dhaulagiri', 6000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('Manaslu', 7000, 'Nepal', NULL);
INSERT INTO public.mountain VALUES ('Nanga Parbat', 9000, 'Pakistan', NULL);
INSERT INTO public.mountain VALUES ('Annapurna', 1000, 'Nepal', NULL);

INSERT INTO public.river VALUES ('Nile', 1000, 'Egypt', 'Cairo,Luxor,Aswan');
INSERT INTO public.river VALUES ('Amazon', 500, 'Brazil', 'Manaus,Belem');
INSERT INTO public.river VALUES ('Yangtze', 300, 'China', 'Shanghai,Wuhan,Chongqing');
INSERT INTO public.river VALUES ('Mississippi', 200, 'United States', 'New Orleans,Memphis,St. Louis');
INSERT INTO public.river VALUES ('Yukon', 400, 'Canada', 'Whitehorse,Dawson City');
INSERT INTO public.river VALUES ('Volga', 800, 'Russia', 'Moscow,Samara,Kazan');
INSERT INTO public.river VALUES ('Mekong', 600, 'Vietnam', 'Ho Chi Minh City,Phnom Penh');
INSERT INTO public.river VALUES ('Danube', 700, 'Germany', 'Passau,Vienna,Budapest');
INSERT INTO public.river VALUES ('Rhine', 900, 'Germany', 'Strasbourg,Frankfurt,Cologne');
INSERT INTO public.river VALUES ('Po', 100, 'Italy', 'Turin,Milan,Venice');

INSERT INTO public.state VALUES ('California', 100000, 10000, 'United States', 'Sacramento', 1000);
INSERT INTO public.state VALUES ('Texas', 50000, 5000, 'United States', 'Austin', 1000);
INSERT INTO public.state VALUES ('Florida', 150000, 15000, 'United States', 'Tallahassee', 1000);
INSERT INTO public.state VALUES ('New York', 200000, 20000, 'United States', 'Albany', 1000);
INSERT INTO public.state VALUES ('Ontario', 80000, 8000, 'Canada', 'Toronto', 1000);
INSERT INTO public.state VALUES ('Sao Paulo', 50000, 6000, 'Brazil', 'Sao Paulo', 1000);
INSERT INTO public.state VALUES ('Guangdong', 200000, 30000, 'China', 'Guangzhou', 1000);
INSERT INTO public.state VALUES ('Maharashtra', 200000, 12000, 'India', 'Mumbai', 1000);
INSERT INTO public.state VALUES ('England', 9000, 10000, 'United Kingdom', 'London', 1000);
INSERT INTO public.state VALUES ('Tokyo', 70000, 50000, 'Japan', 'Tokyo', 1000);
INSERT INTO public.state VALUES ('Ohio', 90000, 11000, 'United States', 'Columbus', 1000);
INSERT INTO public.state VALUES ('Michigan', 120000, 9000, 'United States', 'Lansing', 1000);

