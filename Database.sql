

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";




--
-- Base de données :  `dl_sion_compagnie`
--

-- --------------------------------------------------------

--
-- Structure de la table `achats`
--

DROP TABLE IF EXISTS `achats`;
CREATE TABLE IF NOT EXISTS `achats` (
  `id_achat` int(11) NOT NULL AUTO_INCREMENT,
  `id_fournisseur` int(11) NOT NULL,
  `id_produit` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `prix` int(11) NOT NULL,
  `date_achat` date NOT NULL,
  PRIMARY KEY (`id_achat`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `client`
--

DROP TABLE IF EXISTS `client`;
CREATE TABLE IF NOT EXISTS `client` (
  `id_client` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(250) NOT NULL,
  `prenom` varchar(250) NOT NULL,
  `adresse` varchar(250) NOT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(250) NOT NULL,
  PRIMARY KEY (`id_client`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `facture`
--

DROP TABLE IF EXISTS `facture`;
CREATE TABLE IF NOT EXISTS `facture` (
  `id_facture` int(11) NOT NULL AUTO_INCREMENT,
  `id_client` int(11) NOT NULL,
  `id_ventes` int(11) NOT NULL,
  `numero_F` int(11) NOT NULL,
  `date_fact` int(11) NOT NULL,
  `montant` int(11) NOT NULL,
  `mode_paiment` varchar(250) NOT NULL,
  PRIMARY KEY (`id_facture`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `fournisseur`
--

DROP TABLE IF EXISTS `fournisseur`;
CREATE TABLE IF NOT EXISTS `fournisseur` (
  `id_fournisseur` int(11) NOT NULL AUTO_INCREMENT,
  `nom` varchar(250) NOT NULL,
  `prenom` varchar(250) NOT NULL,
  `adresse` varchar(250) NOT NULL,
  `telephone` int(11) NOT NULL,
  `email` varchar(250) NOT NULL,
  PRIMARY KEY (`id_fournisseur`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `produit`
--

DROP TABLE IF EXISTS `produit`;
CREATE TABLE IF NOT EXISTS `produit` (
  `id_produit` int(11) NOT NULL AUTO_INCREMENT,
  `categorie` varchar(250) NOT NULL,
  `nom_P` varchar(250) NOT NULL,
  `description` text NOT NULL,
  `prix` int(11) NOT NULL,
  `Date_E` date NOT NULL,
  `Date_F` date NOT NULL,
  PRIMARY KEY (`id_produit`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Structure de la table `utilisateur`
--

DROP TABLE IF EXISTS `utilisateur`;
CREATE TABLE IF NOT EXISTS `utilisateur` (
  `id_utilisateur` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(250) NOT NULL,
  `mot_pass` varchar(250) NOT NULL,
  PRIMARY KEY (`id_utilisateur`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `utilisateur`
--


-- --------------------------------------------------------

--
-- Structure de la table `ventes`
--

DROP TABLE IF EXISTS `ventes`;
CREATE TABLE IF NOT EXISTS `ventes` (
  `id_vente` int(11) NOT NULL AUTO_INCREMENT,
  `id_produit` int(11) NOT NULL,
  `id_client` int(11) NOT NULL,
  `quantite` int(11) NOT NULL,
  `prix` int(11) NOT NULL,
  `date_vente` date NOT NULL,
  PRIMARY KEY (`id_vente`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
COMMIT;

ALTER TABLE ventes
ADD CONSTRAINT fk_vente_produit FOREIGN KEY (id_produit) REFERENCES produit(id_produit),
ADD CONSTRAINT fk_vente_client FOREIGN KEY (id_client) REFERENCES client(id_client);

ALTER TABLE achats
ADD CONSTRAINT fk_achat_produit FOREIGN KEY (id_produit) REFERENCES produit(id_produit),
ADD CONSTRAINT fk_achat_fournisseur FOREIGN KEY (id_fournisseur) REFERENCES fournisseur(id_fournisseur);

ALTER TABLE utilisateur
ADD COLUMN image BLOB AFTER mot_pass;
ALTER TABLE produit
ADD COLUMN image BLOB AFTER Date_F;


/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
