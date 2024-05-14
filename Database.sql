-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Hôte : 127.0.0.1:3306
-- Généré le :  sam. 27 avr. 2024 à 11:27
-- Version du serveur :  10.4.10-MariaDB
-- Version de PHP :  7.4.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `dl_sion_compagnie`
--

-- --------------------------------------------------------

--
-- Structure de la table `administrateur`
--

DROP TABLE IF EXISTS `administrateur`;
CREATE TABLE IF NOT EXISTS `administrateur` (
  `id_admin` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(250) NOT NULL,
  `prenom` varchar(250) NOT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(250) NOT NULL,
  `login` varchar(250) NOT NULL,
  `mot_pass` varchar(250) NOT NULL,
  `image` blob DEFAULT NULL,
  PRIMARY KEY (`id_admin`)
) ENGINE=InnoDB;

--
-- Déchargement des données de la table `administrateur`

-- --------------------------------------------------------

--
-- Structure de la table `client`
--

DROP TABLE IF EXISTS `client`;
CREATE TABLE IF NOT EXISTS `client` (
  `id_client` int(11) NOT NULL AUTO_INCREMENT,
  `nom_prenoms` varchar(250) NOT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(250) NOT NULL,
  `adresse` varchar(250) NOT NULL,
  PRIMARY KEY (`id_client`)
) ENGINE=InnoDB;

--
-- Déchargement des données de la table `client`

-- --------------------------------------------------------

--
-- Structure de la table `commande`
--

DROP TABLE IF EXISTS `commande`;
CREATE TABLE IF NOT EXISTS `commande` (
  `id_commande` int(11) NOT NULL AUTO_INCREMENT,
  `id_client` int(11) NOT NULL,
  `id_produit` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `prix_vente` int(11) NOT NULL,
  `date_commande` date NOT NULL,
  `statut` varchar(255) NOT NULL,
  PRIMARY KEY (`id_commande`)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS `entree`;
CREATE TABLE IF NOT EXISTS `entree` (
  `id_entree` int(11) NOT NULL AUTO_INCREMENT,
  `id_fournisseur` int(11) NOT NULL,
  `id_produit` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `prix` int(11) NOT NULL,
  `date_entree` date NOT NULL,
  `statut` varchar(255) NOT NULL,
  PRIMARY KEY (`id_entree`)
) ENGINE=InnoDB;

-- --------------------------------------------------------

--
-- Structure de la table `facture`
--

DROP TABLE IF EXISTS `facture`;
CREATE TABLE IF NOT EXISTS `facture` (
  `id_facture` int(11) NOT NULL AUTO_INCREMENT,
  `id_client` int(11) NOT NULL,
  `id_ventes` int(11) NOT NULL,
  `id_produit` int(11) NOT NULL,
  `numero_F` varchar(255) NOT NULL,
  `reçu` longblob NOT NULL,
  PRIMARY KEY (`id_facture`)
) ENGINE=InnoDB;

-- --------------------------------------------------------

--
-- Structure de la table `fournisseur`
--

DROP TABLE IF EXISTS `fournisseur`;
CREATE TABLE IF NOT EXISTS `fournisseur` (
  `id_fournisseur` int(11) NOT NULL AUTO_INCREMENT,
  `nom_prenoms` varchar(250) NOT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(250) NOT NULL,
  `adresse` varchar(250) NOT NULL,
  PRIMARY KEY (`id_fournisseur`)
) ENGINE=InnoDB;

--
-- Déchargement des données de la table `fournisseur`

-- --------------------------------------------------------

--
-- Structure de la table `produit`
--

DROP TABLE IF EXISTS `produit`;
CREATE TABLE IF NOT EXISTS `produit` (
  `id_produit` int(11) NOT NULL AUTO_INCREMENT,
  `nom_produit` varchar(250) NOT NULL,
  `categorie` varchar(250) NOT NULL,
  `prix` int(11) NOT NULL,
  `stock_min` int(11) DEFAULT NULL,
  `designation` text NOT NULL,
  `image` blob DEFAULT NULL,
  PRIMARY KEY (`id_produit`)
) ENGINE=InnoDB;

--
-- Déchargement des données de la table `produit`

-- --------------------------------------------------------

--
-- Structure de la table `stock`
--

DROP TABLE IF EXISTS `stock`;
CREATE TABLE IF NOT EXISTS `stock` (
  `id_stock` int(11) NOT NULL AUTO_INCREMENT,
  `id_produit` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id_stock`)
) ENGINE=InnoDB;

--
-- Déchargement des données de la table `stock`
--

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
CREATE TABLE IF NOT EXISTS `utilisateur` (
  `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(250) NOT NULL,
  `prenom` varchar(250) NOT NULL,
  `poste` varchar(255) DEFAULT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(250) NOT NULL,
  `login` varchar(250) NOT NULL,
  `mot_pass` varchar(250) NOT NULL,
  `image` blob DEFAULT NULL,
  PRIMARY KEY (`id_utilisateur`)
) ENGINE=InnoDB;

--
-- Déchargement des données de la table `utilisateur`
--
-- --------------------------------------------------------

--
-- Structure de la table `ventes`
--

DROP TABLE IF EXISTS `vente`;
CREATE TABLE IF NOT EXISTS `vente` (
  `id_vente` int(11) NOT NULL AUTO_INCREMENT,
  `id_produit` int(11) NOT NULL,
  `id_client` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `montant` int(11) NOT NULL,
  `date_vente` date NOT NULL,
  PRIMARY KEY (`id_vente`)  
) ENGINE=InnoDB;

ALTER TABLE `vente` ADD `prix_vente` INT NOT NULL AFTER `montant`;
ALTER TABLE `vente` ADD `statut` VARCHAR(250) NOT NULL AFTER `date_vente`;
--
-- Contraintes pour les tables déchargées
--

--
-- Contraintes pour la table `commande`
--

-- Contraintes pour la table `commande`
ALTER TABLE `produit` ADD `stock` INT NOT NULL AFTER `prix`;
--
ALTER TABLE `commande`
  ADD CONSTRAINT `fk_commande_client` FOREIGN KEY (`id_client`) REFERENCES `client` (`id_client`),
  ADD CONSTRAINT `fk_commande_produit` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`);

ALTER TABLE `entree`
  ADD CONSTRAINT `fk_entree_fournisseur` FOREIGN KEY (`id_fournisseur`) REFERENCES `fournisseur` (`id_fournisseur`),
  ADD CONSTRAINT `fk_entree_produit` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`);

--
-- Contraintes pour la table `stock`
--
ALTER TABLE `stock`
  ADD CONSTRAINT `fk_stock` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`);

--
-- Contraintes pour la table `vente`
--
ALTER TABLE `vente`
  ADD CONSTRAINT `fk_vente_client` FOREIGN KEY (`id_client`) REFERENCES `client` (`id_client`),
  ADD CONSTRAINT `fk_vente_produit` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`);

ALTER TABLE `facture`
  ADD CONSTRAINT `fk_facture_client` FOREIGN KEY (`id_client`) REFERENCES `client` (`id_client`),
  ADD CONSTRAINT `fk_facture_produit` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`),
  ADD CONSTRAINT `fk_facture_vente` FOREIGN KEY (`id_ventes`) REFERENCES `vente` (`id_vente`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
