from   utils.generalPurpose import generalPurpose as gp 
from utils.database.database import database
db = database()


query = """DROP TABLE IF EXISTS `brainworks`.`abstracts_temp`"""
db.query(query)

query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`abstracts_temp` LIKE `brainworks`.`abstracts`"""
db.query(query)

query ="""INSERT INTO `brainworks`.`abstracts_temp` 
	(`year`,
	`application_id`,
	`abstract_text`,
	`source`,
	`version`)
SELECT DISTINCT 
	MAX(`abstracts`.`year`), 
	`abstracts`.`application_id`,
	`abstracts`.`abstract_text`,
	MAX(`abstracts`.`source`), 
	MAX(`abstracts`.`version`)
FROM `brainworks`.`abstracts`
GROUP BY 
	`application_id`,
    `abstract_text`"""
db.query(query)


# query ="""RENAME TABLE `abstracts`      TO `abstracts_old`"""
# db.query(query)
# query ="""RENAME TABLE `abstracts_temp` TO `abstracts`"""
# db.query(query)
# query ="""DROP TABLE `abstracts_old`"""
# db.query(query)
  
query ="""DROP TABLE IF EXISTS `brainworks`.`affiliations_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`affiliations_temp` LIKE `brainworks`.`affiliations`"""
db.query(query)

query ="""INSERT INTO `brainworks`.`affiliations_temp`
(`affiliation_num`,
`pub_date`,
`pmid`,
`first_name`,
`last_name`,
`affiliation`)
SELECT DISTINCT
	MAX(`affiliations`.`affiliation_num`),
    MAX(`affiliations`.`pub_date`),
    `affiliations`.`pmid`,
    `affiliations`.`first_name`,
    `affiliations`.`last_name`,
    `affiliations`.`affiliation`
FROM `brainworks`.`affiliations`
GROUP BY 
    `affiliations`.`pmid`,
    `affiliations`.`first_name`,
    `affiliations`.`last_name`,
    `affiliations`.`affiliation`"""
db.query(query)
     
# query ="""RENAME TABLE `affiliations`      TO `affiliations_old`"""
# db.query(query)
# query ="""RENAME TABLE `affiliations_temp` TO `affiliations`"""
# db.query(query)
# query ="""DROP TABLE `affiliations_old`"""
# db.query(query)







query ="""DROP TABLE IF EXISTS `brainworks`.`citations_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`citations_temp` LIKE `brainworks`.`citations`"""
db.query(query)

query ="""INSERT INTO `brainworks`.`citations_temp`
(`pmid`,
`citedby`,
`citation_date`,
`citation_num`)
SELECT DISTINCT 
	`citations`.`pmid`,
    `citations`.`citedby`,
    `citations`.`citation_date`,
    MAX(`citations`.`citation_num`)
FROM `brainworks`.`citations`
GROUP BY
	`citations`.`pmid`,
	`citations`.`citedby`,
    `citations`.`citation_date`"""
db.query(query)

# query ="""RENAME TABLE `citations`      TO `citations_old`"""
# db.query(query)
# query ="""RENAME TABLE `citations_temp` TO `citations`"""
# db.query(query)
# query ="""DROP TABLE `citations_old`"""
# db.query(query)




query ="""DROP TABLE IF EXISTS `brainworks`.`documents_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`documents_temp` LIKE `brainworks`.`documents`"""
db.query(query)

query ="""INSERT INTO `brainworks`.`documents_temp`
(`element_id`,
`pmid`,
`pub_date`,
`content_order`,
`content_type`,
`content`)
SELECT  DISTINCT 
		MAX(`documents`.`element_id`),
	    `documents`.`pmid`,
		`documents`.`pub_date`,
		`documents`.`content_order`,
		`documents`.`content_type`,
		`documents`.`content`
FROM `brainworks`.`documents`
GROUP BY 
`documents`.`pmid`,
`documents`.`pub_date`,
`documents`.`content_order`,
`documents`.`content_type`,
`documents`.`content`"""
db.query(query)

# query ="""RENAME TABLE `documents`      TO `documents_old`"""
# db.query(query)
# query ="""RENAME TABLE `documents_temp` TO `documents`"""
# db.query(query)
# query ="""DROP TABLE `documents_old`"""
# db.query(query)



query ="""DROP TABLE IF EXISTS `brainworks`.`grants_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`grants_temp` LIKE `brainworks`.`grants`"""
db.query(query)   

query ="""INSERT INTO `brainworks`.`grants_temp`
(`grant_num`,
`grant_id`,
`pmid`,
`pub_date`)
SELECT DISTINCT 
       MAX(`grants`.`grant_num`),
       `grants`.`grant_id`,
       `grants`.`pmid`,
       `grants`.`pub_date`
FROM `brainworks`.`grants`
GROUP BY 
`grants`.`grant_id`,
`grants`.`pmid`,
`grants`.`pub_date`"""
db.query(query)

# query ="""RENAME TABLE `grants`      TO `grants_old`"""
# db.query(query)
# query ="""RENAME TABLE `grants_temp` TO `grants`"""
# db.query(query)
# query ="""DROP TABLE `grants_old`"""
# db.query(query)

    
query ="""DROP TABLE IF EXISTS `brainworks`.`id_map_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`id_map_temp` LIKE `brainworks`.`id_map`"""
db.query(query)

  
query ="""INSERT INTO `brainworks`.`id_map_temp`
	(`map_id`,
	`pmid`,
	`pub_date`,
	`pmc_id`,
	`nlm_id`,
	`doi`,
	`issn_linking`)
SELECT DISTINCT 
       MAX(`id_map`.`map_id`),
       `id_map`.`pmid`,
       MAX(`id_map`.`pub_date`),
       MAX(`id_map`.`pmc_id`),
       MAX(`id_map`.`nlm_id`),
       MAX(`id_map`.`doi`),
       MAX(`id_map`.`issn_linking`)
FROM `brainworks`.`id_map`
GROUP BY 
`id_map`.`pmid`"""
db.query(query)

# query ="""RENAME TABLE `id_map`      TO `id_map_old`"""
# db.query(query)
# query ="""RENAME TABLE `id_map_temp` TO `id_map`"""
# db.query(query)
# query ="""DROP TABLE `id_map_old`"""
# db.query(query)




query ="""DROP TABLE IF EXISTS `brainworks`.`link_tables_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`link_tables_temp` LIKE `brainworks`.`link_tables`"""
db.query(query)


query ="""INSERT INTO `brainworks`.`link_tables_temp`
(`year`,
`pmid`,
`project_number`,
`source`,
`version`)
	SELECT DISTINCT `link_tables`.`year`,
    `link_tables`.`pmid`,
    `link_tables`.`project_number`,
    MAX(`link_tables`.`source`),
    MAX(`link_tables`.`version`)
FROM `brainworks`.`link_tables`
GROUP BY
	`link_tables`.`year`,
    `link_tables`.`pmid`,
    `link_tables`.`project_number`"""
db.query(query)

# query = """RENAME TABLE `link_tables`      TO `link_tables_old`"""
# db.query(query)

# query = """RENAME TABLE `link_tables_temp` TO `link_tables`"""
# db.query(query)

# query = """DROP TABLE `link_tables_old`"""
# db.query(query)




query ="""DROP TABLE IF EXISTS `brainworks`.`patents_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`patents_temp` LIKE `brainworks`.`patents`"""
db.query(query)

       
query ="""INSERT INTO `brainworks`.`patents_temp`
(`year`,
`patent_id`,
`patent_title`,
`project_id`,
`patent_org_name`,
`source`,
`version`)
SELECT DISTINCT `patents`.`year`,
    `patents`.`patent_id`,
    `patents`.`patent_title`,
    `patents`.`project_id`,
    `patents`.`patent_org_name`,
    MAX(`patents`.`source`),
    MAX(`patents`.`version`)
FROM `brainworks`.`patents`
GROUP BY 
`patents`.`year`,
`patents`.`patent_id`,
`patents`.`patent_title`,
`patents`.`project_id`,
`patents`.`patent_org_name`"""
db.query(query)

# query ="""RENAME TABLE `patents`      TO `patents_old`"""
# db.query(query)
# query ="""RENAME TABLE `patents_temp` TO `patents`"""
# db.query(query)
# query ="""DROP TABLE `patents_old`"""
# db.query(query)




query ="""DROP TABLE IF EXISTS `brainworks`.`projects_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`projects_temp` LIKE `brainworks`.`projects`"""
db.query(query)
    
query ="""INSERT INTO `brainworks`.`projects_temp`
(`year`,
`application_id`,
`activity`,
`administering_ic`,
`application_type`,
`arra_funded`,
`award_notice_date`,
`budget_start`,
`budget_end`,
`cfda_code`,
`core_project_num`,
`ed_inst_type`,
`foa_number`,
`full_project_num`,
`funding_ics`,
`funding_mechanism`,
`fy`,
`ic_name`,
`nih_spending_cats`,
`org_city`,
`org_country`,
`org_dept`,
`org_district`,
`org_duns`,
`org_fips`,
`org_ipf_code`,
`org_name`,
`org_state`,
`org_zipcode`,
`phr`,
`pi_ids`,
`pi_names`,
`program_officer_name`,
`project_start`,
`project_end`,
`project_terms`,
`project_title`,
`serial_number`,
`study_section`,
`study_section_name`,
`subproject_id`,
`suffix`,
`support_year`,
`direct_cost_amt`,
`indirect_cost_amt`,
`total_cost`,
`total_cost_sub_project`,
`source`,
`version`)
SELECT DISTINCT
	`projects`.`year`,
    `projects`.`application_id`,
    `projects`.`activity`,
    `projects`.`administering_ic`,
    `projects`.`application_type`,
    `projects`.`arra_funded`,
    `projects`.`award_notice_date`,
    `projects`.`budget_start`,
    `projects`.`budget_end`,
    `projects`.`cfda_code`,
    `projects`.`core_project_num`,
    `projects`.`ed_inst_type`,
    `projects`.`foa_number`,
    `projects`.`full_project_num`,
    `projects`.`funding_ics`,
    `projects`.`funding_mechanism`,
    `projects`.`fy`,
    `projects`.`ic_name`,
    `projects`.`nih_spending_cats`,
    `projects`.`org_city`,
    `projects`.`org_country`,
    `projects`.`org_dept`,
    `projects`.`org_district`,
    `projects`.`org_duns`,
    `projects`.`org_fips`,
    `projects`.`org_ipf_code`,
    `projects`.`org_name`,
    `projects`.`org_state`,
    `projects`.`org_zipcode`,
    `projects`.`phr`,
    `projects`.`pi_ids`,
    `projects`.`pi_names`,
    `projects`.`program_officer_name`,
    `projects`.`project_start`,
    `projects`.`project_end`,
    `projects`.`project_terms`,
    `projects`.`project_title`,
    `projects`.`serial_number`,
    `projects`.`study_section`,
    `projects`.`study_section_name`,
    `projects`.`subproject_id`,
    `projects`.`suffix`,
    `projects`.`support_year`,
    `projects`.`direct_cost_amt`,
    `projects`.`indirect_cost_amt`,
    `projects`.`total_cost`,
    `projects`.`total_cost_sub_project`,
    MAX(`projects`.`source`),
    MAX(`projects`.`version`)
FROM `brainworks`.`projects`
GROUP BY 
	`projects`.`year`,
    `projects`.`application_id`,
    `projects`.`activity`,
    `projects`.`administering_ic`,
    `projects`.`application_type`,
    `projects`.`arra_funded`,
    `projects`.`award_notice_date`,
    `projects`.`budget_start`,
    `projects`.`budget_end`,
    `projects`.`cfda_code`,
    `projects`.`core_project_num`,
    `projects`.`ed_inst_type`,
    `projects`.`foa_number`,
    `projects`.`full_project_num`,
    `projects`.`funding_ics`,
    `projects`.`funding_mechanism`,
    `projects`.`fy`,
    `projects`.`ic_name`,
    `projects`.`nih_spending_cats`,
    `projects`.`org_city`,
    `projects`.`org_country`,
    `projects`.`org_dept`,
    `projects`.`org_district`,
    `projects`.`org_duns`,
    `projects`.`org_fips`,
    `projects`.`org_ipf_code`,
    `projects`.`org_name`,
    `projects`.`org_state`,
    `projects`.`org_zipcode`,
    `projects`.`phr`,
    `projects`.`pi_ids`,
    `projects`.`pi_names`,
    `projects`.`program_officer_name`,
    `projects`.`project_start`,
    `projects`.`project_end`,
    `projects`.`project_terms`,
    `projects`.`project_title`,
    `projects`.`serial_number`,
    `projects`.`study_section`,
    `projects`.`study_section_name`,
    `projects`.`subproject_id`,
    `projects`.`suffix`,
    `projects`.`support_year`,
    `projects`.`direct_cost_amt`,
    `projects`.`indirect_cost_amt`,
    `projects`.`total_cost`,
    `projects`.`total_cost_sub_project`"""
db.query(query)

# query ="""RENAME TABLE `projects`      TO `projects_old`"""
# db.query(query)
# query ="""RENAME TABLE `projects_temp` TO `projects`"""
# db.query(query)
# query ="""DROP TABLE `projects_old`"""
# db.query(query)



  
query ="""DROP TABLE IF EXISTS `brainworks`.`publications_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`publications_temp` LIKE `brainworks`.`publications`"""
db.query(query)

query ="""INSERT INTO `brainworks`.`publications_temp`
(`pmid`,
`pub_date`,
`pub_title`,
`country`,
`issn`,
`journal_issue`,
`journal_title`,
`journal_title_abbr`,
`journal_volume`,
`lang`,
`page_number`)
SELECT DISTINCT 
    `publications`.`pmid`,
    `publications`.`pub_date`,
    `publications`.`pub_title`,
    `publications`.`country`,
    `publications`.`issn`,
    `publications`.`journal_issue`,
    `publications`.`journal_title`,
    `publications`.`journal_title_abbr`,
    `publications`.`journal_volume`,
    `publications`.`lang`,
    `publications`.`page_number`
FROM `brainworks`.`publications`"""
db.query(query)

# query ="""RENAME TABLE `publications`      TO `publications_old`"""
# db.query(query)
# query ="""RENAME TABLE `publications_temp` TO `publications`"""
# db.query(query)
# query ="""DROP TABLE `publications_old`"""
# db.query(query)



query ="""DROP TABLE IF EXISTS `brainworks`.`qualifiers_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`qualifiers_temp` LIKE `brainworks`.`qualifiers`"""
db.query(query)


query ="""INSERT INTO `brainworks`.`qualifiers_temp`
(`qualifier_num`,
`pmid`,
`pub_date`,
`topic_id`,
`qualifier_id`,
`description`,
`class`)
SELECT DISTINCT 
    MAX(`qualifiers`.`qualifier_num`),
    `qualifiers`.`pmid`,
    `qualifiers`.`pub_date`,
    `qualifiers`.`topic_id`,
    `qualifiers`.`qualifier_id`,
    `qualifiers`.`description`,
    `qualifiers`.`class`
FROM `brainworks`.`qualifiers`
GROUP BY 
    `qualifiers`.`pmid`,
    `qualifiers`.`pub_date`,
    `qualifiers`.`topic_id`,
    `qualifiers`.`qualifier_id`,
    `qualifiers`.`description`,
    `qualifiers`.`class`"""
db.query(query)

# query ="""RENAME TABLE `qualifiers`      TO `qualifiers_old`"""
# db.query(query)
# query ="""RENAME TABLE `qualifiers_temp` TO `qualifiers`"""
# db.query(query)
# query ="""DROP TABLE `qualifiers_old`"""
# db.query(query)


query ="""DROP TABLE IF EXISTS `brainworks`.`topics_temp`"""
db.query(query)
query ="""CREATE TABLE IF NOT EXISTS `brainworks`.`topics_temp` LIKE `brainworks`.`topics`"""
db.query(query)

query ="""INSERT INTO `brainworks`.`topics_temp`
(`topic_num`,
`pmid`,
`pub_date`,
`source`,
`description`,
`topic_id`,
`class`)
SELECT DISTINCT 
    MAX(`topics`.`topic_num`),
    `topics`.`pmid`,
    `topics`.`pub_date`,
    `topics`.`source`,
    `topics`.`description`,
    `topics`.`topic_id`,
    `topics`.`class`
FROM `brainworks`.`topics`
GROUP BY 
    `topics`.`pmid`,
    `topics`.`pub_date`,
    `topics`.`source`,
    `topics`.`description`,
    `topics`.`topic_id`,
    `topics`.`class`"""
db.query(query)

# query="""RENAME TABLE `topics`      TO `topics_old`"""
# db.query(query)
# query="""RENAME TABLE `topics_temp` TO `topics`"""
# db.query(query)
# query="""DROP TABLE `topics_old`"""
# db.query(query)