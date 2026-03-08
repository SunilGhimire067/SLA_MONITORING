-- MySQL dump 10.13  Distrib 8.0.45, for Linux (aarch64)
--
-- Host: localhost    Database: itsm_db
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `entity_type` varchar(50) NOT NULL,
  `entity_id` int NOT NULL,
  `action` enum('CREATE','UPDATE','DELETE','STATUS_CHANGE','ASSIGN','SLA_BREACH','ESCALATION','LOGIN','LOGOUT') NOT NULL,
  `old_values` json DEFAULT NULL,
  `new_values` json DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(500) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `ix_audit_logs_created_at` (`created_at`),
  KEY `ix_audit_logs_action` (`action`),
  KEY `ix_audit_logs_entity_type` (`entity_type`),
  CONSTRAINT `audit_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_logs`
--

LOCK TABLES `audit_logs` WRITE;
/*!40000 ALTER TABLE `audit_logs` DISABLE KEYS */;
INSERT INTO `audit_logs` VALUES (1,3,'ticket',1,'CREATE',NULL,'{\"title\": \"Current Update of NDC migration and Deadline\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 08:42:39'),(2,3,'ticket',2,'CREATE',NULL,'{\"title\": \"Current Update of NDC migration and Deadline\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 08:43:42'),(3,3,'ticket',3,'CREATE',NULL,'{\"title\": \"DC Service Migration\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 09:04:10'),(4,3,'ticket',4,'CREATE',NULL,'{\"title\": \"DC Service Migration\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 09:04:16'),(5,3,'ticket',5,'CREATE',NULL,'{\"title\": \"DC Service Migration\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 09:04:28'),(6,3,'ticket',6,'CREATE',NULL,'{\"title\": \"DC Service Migration\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 09:05:49'),(7,3,'ticket',7,'CREATE',NULL,'{\"title\": \"NPCI Issue\", \"status\": \"open\", \"priority\": \"P4\"}',NULL,NULL,'2026-03-08 09:11:11'),(8,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"open\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:32:30'),(9,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"in_progress\"}','{\"status\": \"blocked\"}',NULL,NULL,'2026-03-08 09:32:30'),(10,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"blocked\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:32:30'),(11,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"in_progress\"}','{\"status\": \"blocked\"}',NULL,NULL,'2026-03-08 09:32:31'),(12,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"blocked\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:32:32'),(13,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"in_progress\"}','{\"status\": \"blocked\"}',NULL,NULL,'2026-03-08 09:32:32'),(14,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"blocked\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:32:33'),(15,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"in_progress\"}','{\"status\": \"blocked\"}',NULL,NULL,'2026-03-08 09:32:33'),(16,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"blocked\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:32:34'),(17,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"in_progress\"}','{\"status\": \"blocked\"}',NULL,NULL,'2026-03-08 09:32:39'),(18,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"blocked\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:32:41'),(19,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"in_progress\"}','{\"status\": \"blocked\"}',NULL,NULL,'2026-03-08 09:35:09'),(20,4,'ticket',7,'STATUS_CHANGE','{\"status\": \"blocked\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 09:35:09'),(21,5,'ticket',3,'STATUS_CHANGE','{\"status\": \"open\"}','{\"status\": \"in_progress\"}',NULL,NULL,'2026-03-08 10:12:55');
/*!40000 ALTER TABLE `audit_logs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `comments`
--

DROP TABLE IF EXISTS `comments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int NOT NULL,
  `author_id` int NOT NULL,
  `body` text NOT NULL,
  `is_internal` tinyint(1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_comments_author_id` (`author_id`),
  KEY `ix_comments_ticket_id` (`ticket_id`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `tickets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `comments`
--

LOCK TABLES `comments` WRITE;
/*!40000 ALTER TABLE `comments` DISABLE KEYS */;
INSERT INTO `comments` VALUES (1,7,4,'Looking into the issue initial Finding is qr-switch not able to send request to MPA',0,'2026-03-08 09:31:59','2026-03-08 09:31:59'),(2,3,5,'Progress under way; Following modules are migrated and under obervation of Operation Team',0,'2026-03-08 10:12:51','2026-03-08 10:12:51');
/*!40000 ALTER TABLE `comments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `escalation_rules`
--

DROP TABLE IF EXISTS `escalation_rules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `escalation_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `project_id` int DEFAULT NULL,
  `priority` enum('P1','P2','P3','P4') DEFAULT NULL,
  `trigger_type` enum('RESPONSE_BREACH','RESOLUTION_BREACH','APPROACHING_BREACH') NOT NULL,
  `trigger_threshold_minutes` int DEFAULT NULL,
  `escalate_to_user_id` int DEFAULT NULL,
  `escalate_to_team_id` int DEFAULT NULL,
  `notify_channels` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `escalate_to_user_id` (`escalate_to_user_id`),
  KEY `escalate_to_team_id` (`escalate_to_team_id`),
  KEY `ix_escalation_rules_is_active` (`is_active`),
  KEY `ix_escalation_rules_project_id` (`project_id`),
  CONSTRAINT `escalation_rules_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE,
  CONSTRAINT `escalation_rules_ibfk_2` FOREIGN KEY (`escalate_to_user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `escalation_rules_ibfk_3` FOREIGN KEY (`escalate_to_team_id`) REFERENCES `teams` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `escalation_rules`
--

LOCK TABLES `escalation_rules` WRITE;
/*!40000 ALTER TABLE `escalation_rules` DISABLE KEYS */;
/*!40000 ALTER TABLE `escalation_rules` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `ticket_id` int DEFAULT NULL,
  `type` enum('SLA_WARNING','SLA_BREACH','ASSIGNMENT','STATUS_CHANGE','COMMENT','ESCALATION','SYSTEM') NOT NULL,
  `channel` enum('IN_APP','EMAIL','TEAMS') NOT NULL,
  `title` varchar(300) NOT NULL,
  `message` text,
  `is_read` tinyint(1) DEFAULT NULL,
  `sent_at` datetime DEFAULT NULL,
  `read_at` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ticket_id` (`ticket_id`),
  KEY `ix_notifications_user_id` (`user_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`ticket_id`) REFERENCES `tickets` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_permissions_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES (1,'manage_users','Create, edit, delete users','users',NULL),(2,'manage_projects','Create, edit, delete projects','projects',NULL),(3,'manage_teams','Create, edit, delete teams','teams',NULL),(4,'create_tickets','Create new tickets','tickets',NULL),(5,'view_tickets','View tickets and details','tickets',NULL),(6,'manage_sla','Configure SLA policies','sla',NULL),(7,'view_sla','View SLA dashboard','sla',NULL),(8,'view_audit','View audit logs','audit',NULL),(9,'manage_roles','Manage role permissions','roles',NULL);
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `projects`
--

DROP TABLE IF EXISTS `projects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `projects` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `key` varchar(10) NOT NULL,
  `description` text,
  `lead_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_projects_key` (`key`),
  KEY `lead_id` (`lead_id`),
  KEY `ix_projects_is_active` (`is_active`),
  CONSTRAINT `projects_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `projects`
--

LOCK TABLES `projects` WRITE;
/*!40000 ALTER TABLE `projects` DISABLE KEYS */;
INSERT INTO `projects` VALUES (1,'Migration NDC','DEVOPS','The project is for NDC migration: All the service should be exists on the NDC site',NULL,1,'2026-03-08 08:39:21','2026-03-08 08:39:21'),(2,'DC migration','DEVOPS-01','Dc cluster service migration from one cluster to another',NULL,1,'2026-03-08 09:03:21','2026-03-08 09:03:21'),(3,'Support-01','SUPPORT','All Daily Support Task',NULL,1,'2026-03-08 09:08:58','2026-03-08 09:08:58');
/*!40000 ALTER TABLE `projects` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `role_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `role_id` (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (1,1,1),(2,1,2),(3,1,3),(4,1,4),(5,1,5),(6,1,6),(7,1,7),(8,1,8),(9,1,9),(10,2,2),(11,2,3),(12,2,4),(13,2,5),(14,2,6),(15,2,7),(16,2,8),(17,3,4),(18,3,5),(19,3,7),(20,4,5),(21,4,7);
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_roles_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'admin','Super Administrator with full access','2026-03-08 07:05:45'),(2,'manager','Team management and reporting','2026-03-08 08:36:18'),(3,'engineer','Ticket handling and resolution','2026-03-08 08:36:18'),(4,'viewer','Read-only access','2026-03-08 08:36:18');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sla_policies`
--

DROP TABLE IF EXISTS `sla_policies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sla_policies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `priority` enum('P1','P2','P3','P4') NOT NULL,
  `project_id` int DEFAULT NULL,
  `response_time_minutes` int NOT NULL,
  `resolution_time_minutes` int NOT NULL,
  `is_default` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_sla_policies_priority` (`priority`),
  KEY `ix_sla_policies_project_id` (`project_id`),
  CONSTRAINT `sla_policies_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sla_policies`
--

LOCK TABLES `sla_policies` WRITE;
/*!40000 ALTER TABLE `sla_policies` DISABLE KEYS */;
INSERT INTO `sla_policies` VALUES (1,'Default P1 SLA','P1',NULL,15,60,1,1,'2026-03-08 07:07:02','2026-03-08 07:07:02'),(2,'Default P2 SLA','P2',NULL,60,240,1,1,'2026-03-08 07:07:02','2026-03-08 07:07:02'),(3,'Default P3 SLA','P3',NULL,480,1440,1,1,'2026-03-08 07:07:02','2026-03-08 07:07:02'),(4,'Default P4 SLA','P4',NULL,1440,4320,1,1,'2026-03-08 07:07:02','2026-03-08 07:07:02');
/*!40000 ALTER TABLE `sla_policies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sla_records`
--

DROP TABLE IF EXISTS `sla_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sla_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int NOT NULL,
  `sla_policy_id` int NOT NULL,
  `response_deadline` datetime NOT NULL,
  `resolution_deadline` datetime NOT NULL,
  `response_met` tinyint(1) DEFAULT NULL,
  `resolution_met` tinyint(1) DEFAULT NULL,
  `actual_response_minutes` int DEFAULT NULL,
  `actual_resolution_minutes` int DEFAULT NULL,
  `response_breached_at` datetime DEFAULT NULL,
  `resolution_breached_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_id` (`ticket_id`),
  KEY `sla_policy_id` (`sla_policy_id`),
  CONSTRAINT `sla_records_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `tickets` (`id`) ON DELETE CASCADE,
  CONSTRAINT `sla_records_ibfk_2` FOREIGN KEY (`sla_policy_id`) REFERENCES `sla_policies` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sla_records`
--

LOCK TABLES `sla_records` WRITE;
/*!40000 ALTER TABLE `sla_records` DISABLE KEYS */;
INSERT INTO `sla_records` VALUES (1,1,4,'2026-03-09 08:42:39','2026-03-11 08:42:39',NULL,NULL,NULL,NULL,NULL,NULL,'2026-03-08 08:42:39','2026-03-08 08:42:39'),(3,3,4,'2026-03-09 09:04:10','2026-03-11 09:04:10',1,NULL,68,NULL,NULL,NULL,'2026-03-08 09:04:10','2026-03-08 10:12:51'),(7,7,4,'2026-03-09 09:11:11','2026-03-11 09:11:11',1,NULL,20,NULL,NULL,NULL,'2026-03-08 09:11:11','2026-03-08 09:31:59');
/*!40000 ALTER TABLE `sla_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `team_memberships`
--

DROP TABLE IF EXISTS `team_memberships`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `team_memberships` (
  `id` int NOT NULL AUTO_INCREMENT,
  `team_id` int NOT NULL,
  `user_id` int NOT NULL,
  `joined_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `team_id` (`team_id`),
  KEY `ix_team_memberships_user_id` (`user_id`),
  CONSTRAINT `team_memberships_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE CASCADE,
  CONSTRAINT `team_memberships_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `team_memberships`
--

LOCK TABLES `team_memberships` WRITE;
/*!40000 ALTER TABLE `team_memberships` DISABLE KEYS */;
/*!40000 ALTER TABLE `team_memberships` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teams`
--

DROP TABLE IF EXISTS `teams`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teams` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text,
  `lead_id` int DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_teams_lead_id` (`lead_id`),
  CONSTRAINT `teams_ibfk_1` FOREIGN KEY (`lead_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teams`
--

LOCK TABLES `teams` WRITE;
/*!40000 ALTER TABLE `teams` DISABLE KEYS */;
INSERT INTO `teams` VALUES (1,'Migration Task Force','This Team will be responsible for NDC site migration of all services currently existing in DC site',NULL,'2026-03-08 08:40:19','2026-03-08 08:40:19'),(2,'SRE','Need to find and fix the regular issue',NULL,'2026-03-08 09:10:36','2026-03-08 09:10:36');
/*!40000 ALTER TABLE `teams` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tickets`
--

DROP TABLE IF EXISTS `tickets`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tickets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_number` varchar(20) NOT NULL,
  `project_id` int NOT NULL,
  `title` varchar(500) NOT NULL,
  `description` text,
  `priority` enum('P1','P2','P3','P4') NOT NULL,
  `status` enum('OPEN','IN_PROGRESS','BLOCKED','RESOLVED','CLOSED') NOT NULL,
  `reporter_id` int NOT NULL,
  `assignee_id` int DEFAULT NULL,
  `team_id` int DEFAULT NULL,
  `tags` json DEFAULT NULL,
  `first_response_at` datetime DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `closed_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_tickets_ticket_number` (`ticket_number`),
  KEY `team_id` (`team_id`),
  KEY `ix_tickets_project_id` (`project_id`),
  KEY `ix_tickets_status` (`status`),
  KEY `ix_tickets_assignee_id` (`assignee_id`),
  KEY `ix_tickets_reporter_id` (`reporter_id`),
  CONSTRAINT `tickets_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `projects` (`id`),
  CONSTRAINT `tickets_ibfk_2` FOREIGN KEY (`reporter_id`) REFERENCES `users` (`id`),
  CONSTRAINT `tickets_ibfk_3` FOREIGN KEY (`assignee_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  CONSTRAINT `tickets_ibfk_4` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tickets`
--

LOCK TABLES `tickets` WRITE;
/*!40000 ALTER TABLE `tickets` DISABLE KEYS */;
INSERT INTO `tickets` VALUES (1,'DEVOPS-001',1,'Current Update of NDC migration and Deadline','All services should be migrated to NDC with proper verification before Next DR-Drill','P4','OPEN',3,5,1,'null',NULL,NULL,NULL,'2026-03-08 08:42:39','2026-03-08 08:42:39'),(3,'DEVOPS-01-001',2,'DC Service Migration','Convergent and DC cluster Migartion Update and status','P4','IN_PROGRESS',3,5,1,'null','2026-03-08 10:12:51',NULL,NULL,'2026-03-08 09:04:10','2026-03-08 10:12:55'),(7,'SUPPORT-001',3,'NPCI Issue','NPCI is down Need to find the root cause','P4','IN_PROGRESS',3,4,2,'null','2026-03-08 09:31:59',NULL,NULL,'2026-03-08 09:11:11','2026-03-08 09:35:09');
/*!40000 ALTER TABLE `tickets` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `role_id` int NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `avatar_url` varchar(500) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `timezone` varchar(50) DEFAULT NULL,
  `last_login_at` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_is_active` (`is_active`),
  KEY `ix_users_role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (3,'linus.vtcba@gmail.com','$2a$12$rVKw1i.gZFMzOPSoq/b8meLGSA3tMOsLiCKVkhzeW6RCcH9AhlSdG','Super','Admin',1,1,NULL,NULL,'UTC','2026-03-08 11:25:51','2026-03-08 07:05:50','2026-03-08 11:25:51'),(4,'vijaya.khadka@fonepay.com','$2a$12$rVKw1i.gZFMzOPSoq/b8meLGSA3tMOsLiCKVkhzeW6RCcH9AhlSdG','Vijaya','Khadka',3,1,NULL,NULL,'UTC','2026-03-08 09:35:02','2026-03-08 08:36:31','2026-03-08 09:35:02'),(5,'bhuwan.paneru@fonepay.com','$2a$12$rVKw1i.gZFMzOPSoq/b8meLGSA3tMOsLiCKVkhzeW6RCcH9AhlSdG','Bhuwan','Paneru',3,1,NULL,NULL,'UTC','2026-03-08 10:11:57','2026-03-08 08:37:14','2026-03-08 10:11:57'),(6,'sunil.ghimire@fonepay.com','$2a$12$rVKw1i.gZFMzOPSoq/b8meLGSA3tMOsLiCKVkhzeW6RCcH9AhlSdG','Suni','Ghimire',2,1,NULL,NULL,'UTC','2026-03-08 09:42:17','2026-03-08 08:38:08','2026-03-08 09:42:17');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-08 11:26:12
