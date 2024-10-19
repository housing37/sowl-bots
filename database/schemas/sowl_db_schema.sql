-- #===============================================#
-- # init database 'sowl'
-- #===============================================#

-- #===============================================#
-- # clean
-- #===============================================#
-- call DeleteAll_IF_EXISTS('client_shops', 'password37', @result);

-- #===============================================#
-- # create tables
-- #===============================================#
drop table if exists users;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_deleted` timestamp NULL DEFAULT NULL,
  `tg_user_id` varchar(40) NOT NULL, -- ex: '581475171'
  `tg_user_at` varchar(1024) default 'nil_at', -- ex: '@whatever'
  `tg_user_handle` varchar(1024) default 'nil_handle', -- ex: 'bob joe'
--   `tg_user_group_url` varchar(1024) default 'nil_url', -- ex: 't.me/something'

  UNIQUE KEY `ID` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

drop table if exists log_tg_user_at_changes;
CREATE TABLE `log_tg_user_at_changes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_deleted` timestamp NULL DEFAULT NULL,
  `fk_user_id` varchar(40) NOT NULL,
  `tg_user_id_const` varchar(40) NOT NULL,
  `tg_user_at_prev` varchar(40) NOT NULL,
  `tg_user_at_new` varchar(40) NOT NULL,

  UNIQUE KEY `ID` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

drop table if exists user_promotors;
CREATE TABLE `user_promotors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_deleted` timestamp NULL DEFAULT NULL,
  `fk_user_id` varchar(40) NOT NULL,
  `tg_user_group_url` varchar(1024) default 'nil_url', -- ex: 't.me/something'
  `referral_points` INT(10) default 0, -- ex: user_referrals.is_active = True -> pts++, else pts--

  UNIQUE KEY `ID` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

drop table if exists user_referrals;
CREATE TABLE `user_referrals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dt_created` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `dt_deleted` timestamp NULL DEFAULT NULL,
  `fk_user_id` varchar(40) NOT NULL,
  `tg_user_group_url` varchar(1024) default 'nil_url', -- ex: 't.me/something'
  `is_active` BOOLEAN DEFAULT FALSE, -- TRUE = user joined group, FALSE = user left group

  UNIQUE KEY `ID` (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- #===============================================#
-- #===============================================#
