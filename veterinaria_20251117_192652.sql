-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: veterinaria
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
INSERT INTO `auth_group` VALUES (2,'gerente'),(3,'recepcionista'),(1,'veterinario');
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
INSERT INTO `auth_group_permissions` VALUES (73,1,16),(76,1,28),(79,1,32),(77,1,34),(78,1,36),(74,1,42),(75,1,44),(49,2,13),(50,2,14),(51,2,15),(52,2,16),(57,2,25),(58,2,26),(59,2,27),(60,2,28),(69,2,29),(70,2,30),(71,2,31),(72,2,32),(65,2,33),(66,2,34),(67,2,35),(68,2,36),(61,2,37),(62,2,38),(63,2,39),(64,2,40),(53,2,41),(54,2,42),(55,2,43),(56,2,44),(80,3,16),(85,3,25),(86,3,26),(87,3,28),(95,3,30),(96,3,32),(91,3,33),(92,3,34),(93,3,35),(94,3,36),(88,3,37),(89,3,38),(90,3,40),(81,3,41),(82,3,42),(83,3,43),(84,3,44),(97,3,56),(99,3,57),(98,3,60);
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=69 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add cliente',7,'add_cliente'),(26,'Can change cliente',7,'change_cliente'),(27,'Can delete cliente',7,'delete_cliente'),(28,'Can view cliente',7,'view_cliente'),(29,'Can add producto',8,'add_producto'),(30,'Can change producto',8,'change_producto'),(31,'Can delete producto',8,'delete_producto'),(32,'Can view producto',8,'view_producto'),(33,'Can add mascota',9,'add_mascota'),(34,'Can change mascota',9,'change_mascota'),(35,'Can delete mascota',9,'delete_mascota'),(36,'Can view mascota',9,'view_mascota'),(37,'Can add factura',10,'add_factura'),(38,'Can change factura',10,'change_factura'),(39,'Can delete factura',10,'delete_factura'),(40,'Can view factura',10,'view_factura'),(41,'Can add cita',11,'add_cita'),(42,'Can change cita',11,'change_cita'),(43,'Can delete cita',11,'delete_cita'),(44,'Can view cita',11,'view_cita'),(45,'Can add mascota historial archivo',12,'add_mascotahistorialarchivo'),(46,'Can change mascota historial archivo',12,'change_mascotahistorialarchivo'),(47,'Can delete mascota historial archivo',12,'delete_mascotahistorialarchivo'),(48,'Can view mascota historial archivo',12,'view_mascotahistorialarchivo'),(49,'Can add mascota documento',13,'add_mascotadocumento'),(50,'Can change mascota documento',13,'change_mascotadocumento'),(51,'Can delete mascota documento',13,'delete_mascotadocumento'),(52,'Can view mascota documento',13,'view_mascotadocumento'),(53,'Can add Conversación de Chat',14,'add_chatconversation'),(54,'Can change Conversación de Chat',14,'change_chatconversation'),(55,'Can delete Conversación de Chat',14,'delete_chatconversation'),(56,'Can view Conversación de Chat',14,'view_chatconversation'),(57,'Can add Mensaje de Chat',15,'add_chatmessage'),(58,'Can change Mensaje de Chat',15,'change_chatmessage'),(59,'Can delete Mensaje de Chat',15,'delete_chatmessage'),(60,'Can view Mensaje de Chat',15,'view_chatmessage'),(61,'Can add evolucion clinica',16,'add_evolucionclinica'),(62,'Can change evolucion clinica',16,'change_evolucionclinica'),(63,'Can delete evolucion clinica',16,'delete_evolucionclinica'),(64,'Can view evolucion clinica',16,'view_evolucionclinica'),(65,'Can add Perfil de usuario',17,'add_userprofile'),(66,'Can change Perfil de usuario',17,'change_userprofile'),(67,'Can delete Perfil de usuario',17,'delete_userprofile'),(68,'Can view Perfil de usuario',17,'view_userprofile');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (2,'pbkdf2_sha256$600000$lb5z3tPwg0jE9fVvwSY54K$3mU2vVazhpvnushjZKhsNOVGLKofTCRpHVv1KtTekzY=','2025-11-16 04:08:04.150431',1,'admin','','','123@mail.cl',1,1,'2025-10-21 19:49:03.000000'),(6,'pbkdf2_sha256$600000$FrevVln5D5HlJ6YhcsqhSf$qBvdWeDI0j9lAcXillOOXpnxPaqsFSdYlzAWRPNLmbo=','2025-11-14 20:56:23.051275',0,'luisvet','Luis','NAVARRETE','www.er@live.com',0,1,'2025-10-23 02:36:36.000000'),(7,'pbkdf2_sha256$600000$8bJBU0mUYtzX2qXuGLgEgX$gx0fyPGiwn0MrrO9XX0Y1WX5poJRz1Yf1TX9cRASE3A=','2025-11-16 04:08:33.036472',0,'danilo','Danilo','danilo','iaakiko7@gmail.com',0,1,'2025-10-23 05:25:05.849905'),(8,'pbkdf2_sha256$600000$TdL9QpFZf0sZYXfkDeoOcR$RoxZGyMhHqIgAe7ebD6jeo5Lo02j72pLdiVjIDL0Rw0=','2025-10-25 21:10:43.059066',0,'mario','Mario','Espinoza','marioandresespinoza7@gmail.com',0,1,'2025-10-23 20:11:20.323161'),(9,'pbkdf2_sha256$600000$697plg7zzVSuQGI3OSI5BW$kqd3dfYaD5fKwBF/eo73kWwQDZGpuQHl3PrGnY0NvQs=','2025-11-15 01:05:41.755253',0,'tomas','tomas','juan','luisnavarr1999@gmail.com',0,1,'2025-11-04 19:56:17.645918'),(10,'pbkdf2_sha256$600000$Gd8VZP0WrWU0nAeChhuL2L$QEJZs/QmxoYsIvsYrrMR2brDJZhMrJAQVjVD2ITasCs=','2025-11-14 19:27:44.112380',0,'Juanito','juan','juan','www.er@live.com',0,1,'2025-11-14 19:25:29.000000');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
INSERT INTO `auth_user_groups` VALUES (10,6,1),(11,7,3),(9,8,1),(15,9,3),(14,10,2);
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
INSERT INTO `auth_user_user_permissions` VALUES (1,2,1),(2,2,2),(3,2,3),(4,2,4),(5,2,5),(6,2,6),(7,2,7),(8,2,8),(9,2,9),(10,2,10),(11,2,11),(12,2,12),(13,2,13),(14,2,14),(15,2,15),(16,2,16),(17,2,17),(18,2,18),(19,2,19),(20,2,20),(21,2,21),(22,2,22),(23,2,23),(24,2,24),(25,2,25),(26,2,26),(27,2,27),(28,2,28),(29,2,29),(30,2,30),(31,2,31),(32,2,32),(33,2,33),(34,2,34),(35,2,35),(36,2,36),(37,2,37),(38,2,38),(39,2,39),(40,2,40),(41,2,41),(42,2,42),(43,2,43),(44,2,44),(45,2,45),(46,2,46),(47,2,47),(48,2,48);
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
INSERT INTO `django_admin_log` VALUES (1,'2025-10-26 04:36:08.038197','2','123',2,'[{\"changed\": {\"fields\": [\"User permissions\"]}}]',4,2),(2,'2025-10-26 04:39:46.505010','6','luis',2,'[{\"changed\": {\"fields\": [\"User permissions\"]}}]',4,2),(3,'2025-10-26 04:58:06.995420','6','luis',2,'[{\"changed\": {\"fields\": [\"Superuser status\", \"Groups\"]}}]',4,2),(4,'2025-10-26 05:00:56.200540','6','luis',2,'[{\"changed\": {\"fields\": [\"Superuser status\", \"Groups\", \"User permissions\"]}}]',4,2),(5,'2025-10-26 05:02:17.065223','1','veterinario',2,'[{\"changed\": {\"fields\": [\"Permissions\"]}}]',3,2),(6,'2025-10-26 05:02:33.220110','3','recepcionista',2,'[]',3,2),(7,'2025-10-26 05:02:46.842651','2','gerente',2,'[]',3,2),(8,'2025-10-29 02:10:24.274114','1','Mensaje de Cliente en conversación #1',3,'',15,2),(9,'2025-10-29 02:10:28.989996','2','Mensaje de Cliente en conversación #1',3,'',15,2),(10,'2025-10-29 02:10:32.352466','43','Mensaje de Bot en conversación #5',3,'',15,2),(11,'2025-10-29 02:10:34.913106','21','Mensaje de Cliente en conversación #2',3,'',15,2),(12,'2025-10-29 02:10:37.334825','6','Mensaje de Bot en conversación #2',3,'',15,2),(13,'2025-10-29 02:10:40.925612','3','Mensaje de Bot en conversación #1',3,'',15,2),(14,'2025-10-29 02:10:42.992314','4','Mensaje de Cliente en conversación #2',3,'',15,2),(15,'2025-10-29 02:10:46.055500','5','Mensaje de Cliente en conversación #2',3,'',15,2),(16,'2025-10-29 02:25:49.437988','42','Mensaje de Cliente en conversación #5',3,'',15,2),(17,'2025-10-29 02:25:52.337128','18','Mensaje de Bot en conversación #2',3,'',15,2),(18,'2025-10-29 02:25:55.369783','7','Mensaje de Cliente en conversación #2',3,'',15,2),(19,'2025-10-29 02:25:57.849960','8','Mensaje de Bot en conversación #2',3,'',15,2),(20,'2025-10-29 02:26:01.116949','9','Mensaje de Cliente en conversación #2',3,'',15,2),(21,'2025-10-29 02:45:50.382510','4','Conversación #4 (Cerrada)',3,'',14,2),(22,'2025-10-29 02:45:58.109921','5','Conversación #5 (Activa)',3,'',14,2),(23,'2025-10-29 02:46:02.324945','3','Conversación #3 (Cerrada)',3,'',14,2),(24,'2025-10-29 02:46:05.819465','2','Conversación #2 (Pendiente)',3,'',14,2),(25,'2025-10-29 02:46:09.617706','1','Conversación #1 (Pendiente)',3,'',14,2),(26,'2025-10-29 02:59:59.109416','8','Conversación #8 (Cerrada)',3,'',14,2),(27,'2025-10-29 03:00:03.257609','7','Conversación #7 (Cerrada)',3,'',14,2),(28,'2025-10-29 03:00:06.036399','6','Conversación #6 (Cerrada)',3,'',14,2),(29,'2025-10-29 03:19:02.375654','9','Conversación #9 (Cerrada)',3,'',14,2),(30,'2025-10-29 03:19:07.022620','10','Conversación #10 (Activa)',3,'',14,2),(31,'2025-10-29 03:41:32.220305','11','Conversación #11 (Cerrada)',3,'',14,2),(32,'2025-10-29 03:41:36.337442','12','Conversación #12 (Cerrada)',3,'',14,2),(33,'2025-11-04 21:02:03.890254','15','Conversación #15 (Cerrada)',3,'',14,2),(34,'2025-11-04 21:02:06.721532','14','Conversación #14 (Cerrada)',3,'',14,2),(35,'2025-11-04 21:02:08.899904','13','Conversación #13 (Cerrada)',3,'',14,2),(36,'2025-11-04 21:55:11.533064','16','Conversación #16 (Cerrada)',3,'',14,2),(37,'2025-11-04 21:55:14.711780','17','Conversación #17 (Cerrada)',3,'',14,2),(38,'2025-11-04 21:55:16.994648','18','Conversación #18 (Cerrada)',3,'',14,2),(39,'2025-11-04 21:55:18.907369','19','Conversación #19 (Cerrada)',3,'',14,2),(40,'2025-11-04 21:55:20.708811','20','Conversación #20 (Cerrada)',3,'',14,2),(41,'2025-11-14 19:25:29.852635','10','Juanito',1,'[{\"added\": {}}]',4,2),(42,'2025-11-14 19:25:53.269913','10','Juanito',2,'[{\"changed\": {\"fields\": [\"First name\", \"Last name\", \"Email address\", \"Groups\"]}}]',4,2);
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(14,'paneltrabajador','chatconversation'),(15,'paneltrabajador','chatmessage'),(11,'paneltrabajador','cita'),(7,'paneltrabajador','cliente'),(16,'paneltrabajador','evolucionclinica'),(10,'paneltrabajador','factura'),(9,'paneltrabajador','mascota'),(13,'paneltrabajador','mascotadocumento'),(12,'paneltrabajador','mascotahistorialarchivo'),(8,'paneltrabajador','producto'),(17,'paneltrabajador','userprofile'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2025-08-13 23:03:16.885650'),(2,'auth','0001_initial','2025-08-13 23:03:17.149980'),(3,'admin','0001_initial','2025-08-13 23:03:17.215893'),(4,'admin','0002_logentry_remove_auto_add','2025-08-13 23:03:17.221212'),(5,'admin','0003_logentry_add_action_flag_choices','2025-08-13 23:03:17.225927'),(6,'contenttypes','0002_remove_content_type_name','2025-08-13 23:03:17.261906'),(7,'auth','0002_alter_permission_name_max_length','2025-08-13 23:03:17.292504'),(8,'auth','0003_alter_user_email_max_length','2025-08-13 23:03:17.302003'),(9,'auth','0004_alter_user_username_opts','2025-08-13 23:03:17.306666'),(10,'auth','0005_alter_user_last_login_null','2025-08-13 23:03:17.334110'),(11,'auth','0006_require_contenttypes_0002','2025-08-13 23:03:17.336152'),(12,'auth','0007_alter_validators_add_error_messages','2025-08-13 23:03:17.341367'),(13,'auth','0008_alter_user_username_max_length','2025-08-13 23:03:17.350985'),(14,'auth','0009_alter_user_last_name_max_length','2025-08-13 23:03:17.359040'),(15,'auth','0010_alter_group_name_max_length','2025-08-13 23:03:17.366371'),(16,'auth','0011_update_proxy_permissions','2025-08-13 23:03:17.371143'),(17,'auth','0012_alter_user_first_name_max_length','2025-08-13 23:03:17.378421'),(18,'paneltrabajador','0001_initial','2025-08-13 23:03:17.525024'),(19,'paneltrabajador','0002_remove_cita_numero_chip_cita_mascota','2025-08-13 23:03:17.575333'),(20,'paneltrabajador','0003_remove_cita_mascota','2025-08-13 23:03:17.751846'),(21,'paneltrabajador','0004_cita_mascota','2025-08-13 23:03:17.794761'),(22,'paneltrabajador','0005_cita_fecha_alter_cita_cliente','2025-08-13 23:03:17.927211'),(23,'paneltrabajador','0006_alter_cita_n_cita','2025-08-13 23:03:17.966115'),(24,'paneltrabajador','0007_alter_cliente_rut_alter_factura_numero_factura_and_more','2025-08-13 23:03:18.427529'),(25,'paneltrabajador','0008_alter_cliente_rut','2025-08-13 23:03:18.648370'),(26,'paneltrabajador','0009_alter_cliente_rut','2025-08-13 23:03:19.000465'),(27,'paneltrabajador','0010_alter_mascota_numero_chip','2025-08-13 23:03:19.042097'),(28,'paneltrabajador','0011_alter_mascota_numero_chip','2025-08-13 23:03:19.054732'),(29,'paneltrabajador','0012_alter_cita_estado','2025-08-13 23:03:19.061520'),(30,'paneltrabajador','0013_empleado','2025-08-13 23:03:19.116919'),(31,'paneltrabajador','0014_remove_empleado_id_alter_empleado_usuario','2025-08-13 23:03:19.336038'),(32,'paneltrabajador','0015_delete_empleado','2025-08-13 23:03:19.343402'),(33,'paneltrabajador','0016_blogentry','2025-08-13 23:03:19.392416'),(34,'paneltrabajador','0017_delete_blogentry','2025-08-13 23:03:19.399065'),(35,'sessions','0001_initial','2025-08-13 23:03:19.418746'),(36,'paneltrabajador','0018_mascotahistorialarchivo','2025-10-24 05:48:42.335666'),(37,'paneltrabajador','0018_mascota_foto','2025-10-24 19:20:11.915582'),(38,'paneltrabajador','0018_alter_cliente_rut_alter_cliente_telefono','2025-10-24 20:43:42.942520'),(39,'paneltrabajador','0018_cita_asistencia','2025-10-26 03:20:32.559675'),(40,'paneltrabajador','0019_cita_checked_in_at_cita_checked_in_by_and_more','2025-10-26 03:33:47.120699'),(41,'paneltrabajador','0020_mascotadocumento','2025-10-26 06:47:48.204659'),(42,'paneltrabajador','0021_alter_cliente_telefono','2025-10-26 23:31:57.912162'),(43,'paneltrabajador','0021_cita_servicio','2025-10-27 01:05:23.691721'),(44,'paneltrabajador','0022_alter_cliente_telefono','2025-10-28 21:58:14.588514'),(45,'paneltrabajador','0023_alter_cita_estado','2025-10-28 23:58:54.460463'),(46,'paneltrabajador','0024_chatconversation_chatmessage','2025-10-29 00:44:01.665922'),(47,'paneltrabajador','0025_alter_cita_asistencia','2025-11-04 20:36:11.608904'),(48,'paneltrabajador','0026_alter_mascota_historial_medico_evolucionclinica_and_more','2025-11-09 22:58:49.730635'),(49,'paneltrabajador','0027_userprofile','2025-11-14 20:06:54.213221');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('2doqzxihxmooqqffw1f4f16ho63rsbl2','.eJxVjEEOwiAQRe_C2pARmJa6dN8zNAMzSNVAUtqV8e7apAvd_vfef6mJtjVPW5NlmlldVK9Ov1ug-JCyA75TuVUda1mXOehd0Qdteqwsz-vh_h1kavlbR5DOOSAGEeMhoD87kmC582jMYBEjWm-MNThIsikx9sRBXCKA5KJ6fwDbDDf6:1vJfjR:0J26hxpmyTp8FwwUKqq5RG7oOVKHih-r-drnJ0V3Vyw','2025-11-27 22:23:57.898841'),('7pdne627qahsflyxc1n2tn950zc8ekk7','eyJjaGF0Ym90X3BlbmRpbmdfaGFuZG9mZiI6ZmFsc2UsImNoYXRib3RfY29udmVyc2F0aW9uX2lkIjoyNH0:1vGfQa:KcH8UEgQdE5fqeMVArJQQfZDtHKWK8aJjk40D3wpEm8','2025-11-19 15:28:04.213645'),('fsdfqyrqudn1we5da6e8jrurrp9dmwrk','eyJjaGF0Ym90X3BlbmRpbmdfaGFuZG9mZiI6ZmFsc2V9:1vGcqB:XSsbIVBOX6Anweep7XziBKXDBRK8vk_fgpTFcMyoLxA','2025-11-19 12:42:19.114707'),('hdurx3rhurippd55ka9exaxu1y3jtv33','.eJxFyVEOwiAMANC79FsTYbI5LtMUaB3RtAuQGWO8u5--3_cB3Kn3l7WCjTsPHPZghQj5varM59n7IC4t4vmS0nT1qazkQ-CJb8LFwQnyRiPZwJ21VL3jRlpMBKLQs_P_s-nBrdOoplgLRLd8fxnuLKU:1vGOOf:uzfcOnmiuY-wvItGn_SlZp1sMJG8Hpb9CsTrBOYYjJY','2025-11-18 21:16:57.872291'),('itwqatbc1u1tyo1k8810nt58xlqp74im','eyJjaGF0Ym90X3BlbmRpbmdfaGFuZG9mZiI6ZmFsc2UsImNoYXRib3RfY29udmVyc2F0aW9uX2lkIjoxMX0:1vDwlC:nS7GsenCtLjMdsCD_jPJVcz7G1SyeRKl8SzXhqL83iA','2025-11-12 03:22:06.546412'),('ixsii5oojhnaujqcerk6vs25yu3vugyq','e30:1vDWgE:bKRnBjNTuTIf1jmzYT9V8e0V0IwulNRvmqTe4JFsMCc','2025-11-10 23:31:14.377065'),('k7eddjmzxe55sibkm5d5hhxugrq2y76z','eyJjaGF0Ym90X3BlbmRpbmdfaGFuZG9mZiI6ZmFsc2UsImNoYXRib3RfY29udmVyc2F0aW9uX2lkIjoxNH0:1vE5S0:mIZ2ZR__1s5xpZEYa6lhSu9icTAoVKTIKOisSWAB53g','2025-11-12 12:38:52.418171'),('mqkba594cf3k6u8xjhieg65lx3cgqnut','eyJjaGF0Ym90X3BlbmRpbmdfaGFuZG9mZiI6ZmFsc2UsImNoYXRib3RfY29udmVyc2F0aW9uX2lkIjoyOH0:1vJ9hx:8stovJJPr2aphHhw4lByR0v50Ow4KDVsElPQp_EwEmU','2025-11-26 12:12:17.172220'),('o78lenolz5pjbsepqqe9hxdpl3x1yjjy','e30:1vDCgS:3EUlYziv32tWtZSXgnHfEGt2f8zFgdzT49t2dm7y2BM','2025-11-10 02:10:08.128486'),('v014kj1oxsdlqvpowitlsc5m3ndcr3cn','eyJyZXNlcnZhX2NfcnV0IjoyMTQ5OTIzODg4LCJyZXNlcnZhX21faWQiOiIyNyJ9:1vD3mV:EiWli_F0GHTkD33IUChZzLK-f-ywjHOxJMWFnkaKEyA','2025-11-09 16:39:47.066275'),('xzghur97ihr3jez4ri0f450kmer8j1zg','.eJxVjEEOwiAQRe_C2pARmJa6dN8zNAMzSNVAUtqV8e7apAvd_vfef6mJtjVPW5NlmlldVK9Ov1ug-JCyA75TuVUda1mXOehd0Qdteqwsz-vh_h1kavlbR5DOOSAGEeMhoD87kmC582jMYBEjWm-MNThIsikx9sRBXCKA5KJ6fwDbDDf6:1vKU41:8lQtpmnBVkVX8NjkEV4IDVi27ApESdKCfix-U-ppqaM','2025-11-30 04:08:33.038922'),('y9rr6bvxbkmwmdq3ijl4gmrez91hbiu8','e30:1vDCDW:0HS5f6Rtj-SuTTcBWB3z-gBoX_rKhU974HWKWcuulsU','2025-11-10 01:40:14.306448');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_chatconversation`
--

DROP TABLE IF EXISTS `paneltrabajador_chatconversation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_chatconversation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `source` varchar(30) NOT NULL,
  `initial_question` longtext NOT NULL,
  `state` varchar(20) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  `last_message_at` datetime(6) NOT NULL,
  `last_message_preview` varchar(255) NOT NULL,
  `assigned_to_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paneltrabajador_chat_assigned_to_id_82725ef2_fk_auth_user` (`assigned_to_id`),
  CONSTRAINT `paneltrabajador_chat_assigned_to_id_82725ef2_fk_auth_user` FOREIGN KEY (`assigned_to_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_chatconversation`
--

LOCK TABLES `paneltrabajador_chatconversation` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_chatconversation` DISABLE KEYS */;
INSERT INTO `paneltrabajador_chatconversation` VALUES (21,'web','oaasa','closed','2025-11-04 21:59:40.784906','2025-11-04 22:05:23.635584','2025-11-04 21:59:40.793279','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.',2),(22,'web','fsdf','closed','2025-11-04 22:59:24.613353','2025-11-04 23:00:08.036334','2025-11-04 23:00:08.036240','que tenga un buen dia',2),(23,'web','en nada eres inutil','closed','2025-11-05 12:18:17.531719','2025-11-05 12:21:19.118291','2025-11-05 12:21:19.118144','chao chao',7),(24,'web','placeholder','closed','2025-11-05 15:22:17.614005','2025-11-05 15:33:32.852300','2025-11-05 15:33:32.852197','alo',7),(25,'web','ewfasdfasf','closed','2025-11-10 00:54:52.890719','2025-11-10 00:54:59.723289','2025-11-10 00:54:59.723243','hola',7),(26,'web','necesito asistencia','closed','2025-11-10 01:37:02.109890','2025-11-10 01:37:34.134807','2025-11-10 01:37:34.134764','chao',7),(27,'web','ALOO','closed','2025-11-12 12:11:06.538100','2025-11-12 12:16:07.167981','2025-11-12 12:16:07.167856','muy talde',7),(28,'web','alo','closed','2025-11-12 12:12:17.139583','2025-11-12 12:16:24.165956','2025-11-12 12:16:24.165878','no hay',7);
/*!40000 ALTER TABLE `paneltrabajador_chatconversation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_chatmessage`
--

DROP TABLE IF EXISTS `paneltrabajador_chatmessage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_chatmessage` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `author` varchar(20) NOT NULL,
  `content` longtext NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `conversation_id` bigint(20) NOT NULL,
  `staff_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paneltrabajador_chat_conversation_id_0ea513c9_fk_paneltrab` (`conversation_id`),
  KEY `paneltrabajador_chat_staff_user_id_a2b46bee_fk_auth_user` (`staff_user_id`),
  CONSTRAINT `paneltrabajador_chat_conversation_id_0ea513c9_fk_paneltrab` FOREIGN KEY (`conversation_id`) REFERENCES `paneltrabajador_chatconversation` (`id`),
  CONSTRAINT `paneltrabajador_chat_staff_user_id_a2b46bee_fk_auth_user` FOREIGN KEY (`staff_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=213 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_chatmessage`
--

LOCK TABLES `paneltrabajador_chatmessage` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_chatmessage` DISABLE KEYS */;
INSERT INTO `paneltrabajador_chatmessage` VALUES (151,'client','oaasa','2025-11-04 21:59:40.786551',21,NULL),(152,'client','Sí quiero hablar con la recepción','2025-11-04 21:59:40.788967',21,NULL),(153,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-04 21:59:40.792265',21,NULL),(154,'client','fsdf','2025-11-04 22:59:24.614929',22,NULL),(155,'client','Sí quiero hablar con la recepción','2025-11-04 22:59:24.620902',22,NULL),(156,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-04 22:59:24.623219',22,NULL),(157,'staff','olaaaa','2025-11-04 22:59:34.320324',22,2),(158,'client','alooooo','2025-11-04 22:59:40.634757',22,NULL),(159,'client','alooo','2025-11-04 22:59:52.507979',22,NULL),(160,'client','paso algo??','2025-11-04 22:59:54.990464',22,NULL),(161,'staff','que tenga un buen dia','2025-11-04 23:00:08.033824',22,2),(162,'client','en nada eres inutil','2025-11-05 12:18:17.538657',23,NULL),(163,'client','Sí quiero hablar con la recepción','2025-11-05 12:18:17.551143',23,NULL),(164,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-05 12:18:17.559245',23,NULL),(165,'client','ya pero rapido','2025-11-05 12:18:37.416724',23,NULL),(166,'bot','Nuestro equipo de recepción ya está al tanto de tu consulta. Mantén esta ventana abierta y te escribirán a la brevedad.','2025-11-05 12:18:37.432964',23,NULL),(167,'client','no pero mas rapido','2025-11-05 12:18:44.573195',23,NULL),(168,'bot','Nuestro equipo de recepción ya está al tanto de tu consulta. Mantén esta ventana abierta y te escribirán a la brevedad.','2025-11-05 12:18:44.595750',23,NULL),(169,'staff','oe yapo callate','2025-11-05 12:18:46.733930',23,7),(170,'client','ya ya qe wea pasa','2025-11-05 12:18:55.439980',23,NULL),(171,'client','trans','2025-11-05 12:18:58.413853',23,NULL),(172,'staff','a 500 lo anticucho de perro','2025-11-05 12:19:11.599761',23,7),(173,'client','pero a mi me gustsan de gato+','2025-11-05 12:19:59.584395',23,NULL),(174,'staff','calajo','2025-11-05 12:20:11.000924',23,7),(175,'client','ya me aburriste','2025-11-05 12:21:08.757529',23,NULL),(176,'client','eliminame','2025-11-05 12:21:10.394020',23,NULL),(177,'staff','chao chao','2025-11-05 12:21:19.109248',23,7),(178,'client','placeholder','2025-11-05 15:22:17.619518',24,NULL),(179,'client','Sí quiero hablar con la recepción','2025-11-05 15:22:17.628499',24,NULL),(180,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-05 15:22:17.634247',24,NULL),(181,'staff','wena','2025-11-05 15:22:23.769097',24,7),(182,'client','alo','2025-11-05 15:22:29.902274',24,NULL),(183,'staff','aloooo','2025-11-05 15:22:35.530182',24,7),(184,'client','como esta','2025-11-05 15:22:49.041896',24,NULL),(185,'client','yo bn','2025-11-05 15:22:50.370787',24,NULL),(186,'staff','a 500 los anticuhcos de perro','2025-11-05 15:22:52.858694',24,7),(187,'client','y usted','2025-11-05 15:22:54.809466',24,NULL),(188,'client','justo se murio el mio','2025-11-05 15:23:03.686845',24,NULL),(189,'staff','alo','2025-11-05 15:33:32.844469',24,7),(190,'client','ewfasdfasf','2025-11-10 00:54:52.894778',25,NULL),(191,'client','Sí quiero hablar con la recepción','2025-11-10 00:54:52.898176',25,NULL),(192,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-10 00:54:52.900287',25,NULL),(193,'staff','hola','2025-11-10 00:54:59.721238',25,7),(194,'client','necesito asistencia','2025-11-10 01:37:02.111315',26,NULL),(195,'client','Sí quiero hablar con la recepción','2025-11-10 01:37:02.115735',26,NULL),(196,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-10 01:37:02.120561',26,NULL),(197,'staff','chao','2025-11-10 01:37:34.133568',26,7),(198,'client','ALOO','2025-11-12 12:11:06.548387',27,NULL),(199,'client','Sí quiero hablar con la recepción','2025-11-12 12:11:06.557103',27,NULL),(200,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-12 12:11:06.564606',27,NULL),(201,'client','si','2025-11-12 12:11:11.793450',27,NULL),(202,'bot','Nuestro equipo de recepción ya está al tanto de tu consulta. Mantén esta ventana abierta y te escribirán a la brevedad.','2025-11-12 12:11:11.808669',27,NULL),(203,'client','alo','2025-11-12 12:12:17.143827',28,NULL),(204,'client','si','2025-11-12 12:12:17.154456',28,NULL),(205,'bot','Perfecto, avisaremos a nuestra recepción para que continúe la conversación. Te contactarán en este chat.','2025-11-12 12:12:17.164806',28,NULL),(206,'staff','hola','2025-11-12 12:12:39.522070',28,7),(207,'staff','bienvenido a la vet de arce','2025-11-12 12:12:49.226250',28,7),(208,'client','hola gracias','2025-11-12 12:12:59.043451',28,NULL),(209,'client','quiero pedir hora','2025-11-12 12:13:06.778964',28,NULL),(210,'staff','holaaa','2025-11-12 12:15:55.387318',27,7),(211,'client','muy talde','2025-11-12 12:16:07.156614',27,NULL),(212,'staff','no hay','2025-11-12 12:16:24.159349',28,7);
/*!40000 ALTER TABLE `paneltrabajador_chatmessage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_cita`
--

DROP TABLE IF EXISTS `paneltrabajador_cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_cita` (
  `n_cita` int(11) NOT NULL AUTO_INCREMENT,
  `estado` varchar(1) NOT NULL,
  `cliente_id` varchar(12) DEFAULT NULL,
  `usuario_id` int(11) NOT NULL,
  `mascota_id` int(11) DEFAULT NULL,
  `fecha` datetime(6) NOT NULL,
  `asistencia` varchar(1) DEFAULT NULL,
  `checked_in_at` datetime(6) DEFAULT NULL,
  `checked_in_by_id` int(11) DEFAULT NULL,
  `servicio` varchar(20) NOT NULL,
  PRIMARY KEY (`n_cita`),
  KEY `paneltrabajador_cita_usuario_id_2fce841e_fk_auth_user_id` (`usuario_id`),
  KEY `paneltrabajador_cita_mascota_id_54c117c5_fk` (`mascota_id`),
  KEY `paneltrabajador_cita_cliente_id_c1587657_fk` (`cliente_id`),
  KEY `paneltrabajador_cita_checked_in_by_id_c0b029a3_fk_auth_user_id` (`checked_in_by_id`),
  CONSTRAINT `paneltrabajador_cita_checked_in_by_id_c0b029a3_fk_auth_user_id` FOREIGN KEY (`checked_in_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `paneltrabajador_cita_cliente_id_c1587657_fk` FOREIGN KEY (`cliente_id`) REFERENCES `paneltrabajador_cliente` (`rut`),
  CONSTRAINT `paneltrabajador_cita_mascota_id_54c117c5_fk` FOREIGN KEY (`mascota_id`) REFERENCES `paneltrabajador_mascota` (`id_mascota`),
  CONSTRAINT `paneltrabajador_cita_usuario_id_2fce841e_fk_auth_user_id` FOREIGN KEY (`usuario_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_cita`
--

LOCK TABLES `paneltrabajador_cita` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_cita` DISABLE KEYS */;
INSERT INTO `paneltrabajador_cita` VALUES (61,'1','10540675',6,53,'2025-10-04 23:17:00.000000','A','2025-11-04 23:19:37.400069',7,'general'),(62,'1','12856851',6,50,'2024-02-04 23:19:00.000000','N',NULL,NULL,'dentista'),(63,'3',NULL,6,NULL,'2025-11-07 23:14:00.000000',NULL,NULL,NULL,'dentista'),(64,'2','20329848',8,51,'2025-11-05 23:14:00.000000',NULL,NULL,NULL,'cirugia'),(65,'2','60033773',9,52,'2025-11-04 23:26:00.000000',NULL,NULL,NULL,'dentista'),(66,'3',NULL,6,NULL,'2025-11-04 23:37:00.000000',NULL,NULL,NULL,'dentista'),(67,'3',NULL,6,NULL,'2025-11-04 23:38:00.000000',NULL,NULL,NULL,'cirugia'),(68,'2','30554752',6,54,'2025-11-10 12:40:00.000000',NULL,NULL,NULL,'general'),(69,'1','20561714',6,55,'2025-11-06 15:24:00.000000','N',NULL,NULL,'general'),(70,'1','12856851',6,50,'2025-11-11 03:16:00.000000','N',NULL,NULL,'general'),(71,'1','12856851',6,50,'2025-11-14 20:22:00.000000','P',NULL,NULL,'cirugia'),(72,'2','19187433',6,56,'2025-11-14 20:23:00.000000',NULL,NULL,NULL,'general'),(74,'1','12856851',6,50,'2025-11-11 01:04:00.000000','N',NULL,NULL,'general'),(75,'1','12856851',6,50,'2025-11-11 01:04:00.000000','A','2025-11-11 03:04:11.230682',7,'general'),(76,'1','12856851',6,50,'2025-11-12 12:03:00.000000','A','2025-11-12 12:04:02.223492',7,'dentista'),(77,'1','12856851',6,58,'2025-11-12 00:01:00.000000','N',NULL,NULL,'dentista'),(78,'3',NULL,6,NULL,'2025-11-12 03:34:00.000000',NULL,NULL,NULL,'cirugia'),(79,'2','23833686',6,59,'2025-11-13 12:17:00.000000',NULL,NULL,NULL,'dentista'),(80,'3',NULL,6,NULL,'2025-11-12 03:25:00.000000',NULL,NULL,NULL,'general'),(81,'3',NULL,6,NULL,'2025-11-12 03:30:00.000000',NULL,NULL,NULL,'general'),(82,'3',NULL,6,NULL,'2025-11-12 04:31:00.000000',NULL,NULL,NULL,'general'),(83,'3',NULL,6,NULL,'2025-11-12 13:29:00.000000',NULL,NULL,NULL,'cirugia'),(84,'3',NULL,6,NULL,'2025-11-12 04:32:00.000000',NULL,NULL,NULL,'dentista'),(85,'2','23833686',6,59,'2025-11-12 15:32:00.000000',NULL,NULL,NULL,'general'),(86,'3',NULL,6,NULL,'2025-11-12 16:33:00.000000',NULL,NULL,NULL,'dentista'),(87,'3',NULL,6,NULL,'2025-11-14 21:20:00.000000',NULL,NULL,NULL,'general'),(88,'3',NULL,6,NULL,'2025-11-14 22:24:00.000000',NULL,NULL,NULL,'dentista'),(89,'1','12856851',6,50,'2025-11-20 20:08:00.000000','P',NULL,NULL,'general'),(90,'3',NULL,6,NULL,'2025-11-16 22:44:00.000000',NULL,NULL,NULL,'general');
/*!40000 ALTER TABLE `paneltrabajador_cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_cliente`
--

DROP TABLE IF EXISTS `paneltrabajador_cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_cliente` (
  `rut` varchar(12) NOT NULL,
  `nombre_cliente` varchar(150) NOT NULL,
  `direccion` varchar(65) NOT NULL,
  `telefono` varchar(12) NOT NULL,
  `email` varchar(254) NOT NULL,
  PRIMARY KEY (`rut`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_cliente`
--

LOCK TABLES `paneltrabajador_cliente` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_cliente` DISABLE KEYS */;
INSERT INTO `paneltrabajador_cliente` VALUES ('10540675','rosa','las flores 456','+56923543534','luisnavarr1999@gmail.com'),('12856851','juan','pasaje las casas 123','+56974387458','luisnavarr1999@gmail.com'),('19187433','Alberto','los alber 123','+56983474343','www.er@live.com'),('20329848','Tomas','Pasaje Rigel','+56923423432','www.er@live.com'),('20561714','marserdo','calle nueva','+56986265232','marcelo.ponce07@inacapmail.cl'),('23833686','pepito','casa de peito','+56909877890','marioandresespinoza7@gmail.com'),('24691543','Ricardo','pasaje los tomas','+56912312321','www.er@live.com'),('30554752','Mario','Mario casa 2','+56975938338','marioandresespinoza7@gmail.com'),('60033773','Anibal','las casitas 123','+56923543564','www.er@live.com');
/*!40000 ALTER TABLE `paneltrabajador_cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_evolucionclinica`
--

DROP TABLE IF EXISTS `paneltrabajador_evolucionclinica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_evolucionclinica` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `servicio` varchar(20) NOT NULL,
  `resumen` varchar(255) NOT NULL,
  `detalle` longtext NOT NULL,
  `recomendaciones` longtext NOT NULL,
  `creado_en` datetime(6) NOT NULL,
  `cita_id` int(11) DEFAULT NULL,
  `mascota_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `paneltrabajador_evol_cita_id_caaa5e76_fk_paneltrab` (`cita_id`),
  KEY `paneltrabajador_evol_mascota_id_716afc7e_fk_paneltrab` (`mascota_id`),
  CONSTRAINT `paneltrabajador_evol_cita_id_caaa5e76_fk_paneltrab` FOREIGN KEY (`cita_id`) REFERENCES `paneltrabajador_cita` (`n_cita`),
  CONSTRAINT `paneltrabajador_evol_mascota_id_716afc7e_fk_paneltrab` FOREIGN KEY (`mascota_id`) REFERENCES `paneltrabajador_mascota` (`id_mascota`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_evolucionclinica`
--

LOCK TABLES `paneltrabajador_evolucionclinica` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_evolucionclinica` DISABLE KEYS */;
INSERT INTO `paneltrabajador_evolucionclinica` VALUES (3,'general','dolores de patitas','se hizo el examen y analiso las radiografias','descanzar y dar pastillas','2025-11-10 00:39:47.158717',61,53),(4,'general','dolores de patitas','sdfdsfdsfdsdsf','tome pastillas','2025-11-10 01:11:58.589192',72,56),(5,'general','prueba 1','preuba','si','2025-11-11 02:03:55.607932',72,56),(6,'general','prueba 2','si','no','2025-11-11 02:04:19.598248',72,56),(7,'cirugia','prueba 1','si','no','2025-11-11 02:04:49.122669',71,50),(8,'general','prueba 2','si','no','2025-11-11 02:04:59.652481',70,50),(9,'dentista','test','test','test','2025-11-15 05:24:28.259381',76,50);
/*!40000 ALTER TABLE `paneltrabajador_evolucionclinica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_factura`
--

DROP TABLE IF EXISTS `paneltrabajador_factura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_factura` (
  `numero_factura` int(11) NOT NULL AUTO_INCREMENT,
  `total_pagar` int(11) NOT NULL,
  `detalle` longtext NOT NULL,
  `estado_pago` varchar(1) NOT NULL,
  `cliente_id` varchar(12) NOT NULL,
  PRIMARY KEY (`numero_factura`),
  KEY `paneltrabajador_factura_cliente_id_75f6caf8_fk` (`cliente_id`),
  CONSTRAINT `paneltrabajador_factura_cliente_id_75f6caf8_fk` FOREIGN KEY (`cliente_id`) REFERENCES `paneltrabajador_cliente` (`rut`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_factura`
--

LOCK TABLES `paneltrabajador_factura` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_factura` DISABLE KEYS */;
/*!40000 ALTER TABLE `paneltrabajador_factura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_mascota`
--

DROP TABLE IF EXISTS `paneltrabajador_mascota`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_mascota` (
  `id_mascota` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(150) NOT NULL,
  `numero_chip` bigint(20) NOT NULL,
  `especie` varchar(50) NOT NULL,
  `raza` varchar(50) NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `historial_medico` longtext NOT NULL,
  `cliente_id` varchar(12) NOT NULL,
  PRIMARY KEY (`id_mascota`),
  UNIQUE KEY `paneltrabajador_mascota_numero_chip_464450c7_uniq` (`numero_chip`),
  KEY `paneltrabajador_mascota_cliente_id_0d9342a9_fk` (`cliente_id`),
  CONSTRAINT `paneltrabajador_mascota_cliente_id_0d9342a9_fk` FOREIGN KEY (`cliente_id`) REFERENCES `paneltrabajador_cliente` (`rut`)
) ENGINE=InnoDB AUTO_INCREMENT=60 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_mascota`
--

LOCK TABLES `paneltrabajador_mascota` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_mascota` DISABLE KEYS */;
INSERT INTO `paneltrabajador_mascota` VALUES (50,'firulais',6756,'Perro','Mestizo','2025-06-17','','12856851'),(51,'Chip',576567,'Gato','Maine Coon','2025-06-10','','20329848'),(52,'motita',789879,'Otros','Hámster','2025-08-06','','60033773'),(53,'Jamon',8976,'Otros','Erizo','2025-07-02','','10540675'),(54,'luis',1235,'Perro','Pug','2025-06-04','','30554752'),(55,'marselo jr',1313,'Otros','Pez','2002-06-01','ta enfermito','20561714'),(56,'Salchi',3455,'Perro','Mestizo','2022-02-17','ddsfdsfdsfds','19187433'),(58,'tomacito',3435,'Perro','Mestizo','2024-12-11','','12856851'),(59,'peito',1234,'Perro','Golden Retriever','2025-03-21','','23833686');
/*!40000 ALTER TABLE `paneltrabajador_mascota` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_mascotadocumento`
--

DROP TABLE IF EXISTS `paneltrabajador_mascotadocumento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_mascotadocumento` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `archivo` varchar(100) NOT NULL,
  `subido_en` datetime(6) NOT NULL,
  `mascota_id` int(11) NOT NULL,
  `evolucion_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `paneltrabajador_masc_mascota_id_78e33c82_fk_paneltrab` (`mascota_id`),
  KEY `paneltrabajador_masc_evolucion_id_bbdbb432_fk_paneltrab` (`evolucion_id`),
  CONSTRAINT `paneltrabajador_masc_evolucion_id_bbdbb432_fk_paneltrab` FOREIGN KEY (`evolucion_id`) REFERENCES `paneltrabajador_evolucionclinica` (`id`),
  CONSTRAINT `paneltrabajador_masc_mascota_id_78e33c82_fk_paneltrab` FOREIGN KEY (`mascota_id`) REFERENCES `paneltrabajador_mascota` (`id_mascota`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_mascotadocumento`
--

LOCK TABLES `paneltrabajador_mascotadocumento` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_mascotadocumento` DISABLE KEYS */;
INSERT INTO `paneltrabajador_mascotadocumento` VALUES (27,'mascotas/documentos/radiografia_mascota.png','2025-11-10 00:39:47.163635',53,3),(28,'mascotas/documentos/radiografia_mascota_jpD3WRo.png','2025-11-10 01:11:58.593840',56,4),(29,'mascotas/documentos/Ficha_Clinica_Veterinaria_de_Arce.pdf','2025-11-10 01:12:49.575483',56,NULL),(30,'mascotas/documentos/radiografia_mascota_3stgI3l.png','2025-11-11 02:03:55.613789',56,5),(31,'mascotas/documentos/radiografia_mascota_PE39HZD.png','2025-11-11 02:04:19.602084',56,6),(32,'mascotas/documentos/radiografia_mascota.png','2025-11-15 05:23:17.521433',50,7);
/*!40000 ALTER TABLE `paneltrabajador_mascotadocumento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_producto`
--

DROP TABLE IF EXISTS `paneltrabajador_producto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_producto` (
  `id_producto` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_producto` varchar(30) NOT NULL,
  `stock_disponible` int(11) NOT NULL,
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_producto`
--

LOCK TABLES `paneltrabajador_producto` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_producto` DISABLE KEYS */;
INSERT INTO `paneltrabajador_producto` VALUES (1,'Vacunas',45);
/*!40000 ALTER TABLE `paneltrabajador_producto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paneltrabajador_userprofile`
--

DROP TABLE IF EXISTS `paneltrabajador_userprofile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `paneltrabajador_userprofile` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `photo` varchar(100) DEFAULT NULL,
  `updated_at` datetime(6) NOT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `paneltrabajador_userprofile_user_id_c278cb19_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paneltrabajador_userprofile`
--

LOCK TABLES `paneltrabajador_userprofile` WRITE;
/*!40000 ALTER TABLE `paneltrabajador_userprofile` DISABLE KEYS */;
INSERT INTO `paneltrabajador_userprofile` VALUES (1,'panel/perfiles/fondo-login.jpg','2025-11-14 20:36:17.318971',2),(2,'panel/perfiles/Gemini_Generated_Image_i91ub0i91ub0i91u.jpg','2025-11-14 20:56:36.723087',6),(3,'','2025-11-15 21:25:06.644078',9);
/*!40000 ALTER TABLE `paneltrabajador_userprofile` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-11-17 16:26:52
