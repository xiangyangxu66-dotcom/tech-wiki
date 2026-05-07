-- ============================================================================
-- Tech-Wiki DB Schema (Pure SQL DDL)
-- MySQL 8.0+
-- 本スキーマは Django models.py の構造に同期しています。
-- initdb 用：MySQL コンテナ初回起動時に自動実行。
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. Category（カテゴリ）— MPTT ツリー構造
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wiki_category (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    slug        VARCHAR(200) NOT NULL,
    parent_id   BIGINT       NULL,
    lft         INT UNSIGNED NOT NULL,
    rght        INT UNSIGNED NOT NULL,
    tree_id     INT UNSIGNED NOT NULL,
    level       INT UNSIGNED NOT NULL DEFAULT 0,
    description LONGTEXT     NOT NULL,
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    UNIQUE KEY uk_wiki_category_slug (slug),
    INDEX      ix_wiki_category_parent_id (parent_id),
    INDEX      ix_wiki_category_tree    (tree_id, lft),
    CONSTRAINT fk_category_parent FOREIGN KEY (parent_id)
        REFERENCES wiki_category(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 2. Note（技術ノート）
--    content  : Markdown 本文（LONGTEXT）
--    note_tags: YAML frontmatter から自動抽出されたタグ配列（JSON）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wiki_note (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(500) NOT NULL,
    slug        VARCHAR(255) NOT NULL,
    content     LONGTEXT     NOT NULL,
    note_tags   JSON         NULL,             -- JSON配列: ["tag1","tag2"]
    category_id BIGINT       NULL,
    bookmark    TINYINT(1)   NOT NULL DEFAULT 0,
    status      VARCHAR(20)  NOT NULL DEFAULT 'draft',
    created_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),

    UNIQUE KEY  uk_wiki_note_slug  (slug),
    INDEX       ix_wiki_note_category_id (category_id),
    INDEX       ix_wiki_note_status      (status),
    INDEX       ix_wiki_note_bookmark    (bookmark),
    INDEX       ix_wiki_note_updated_at  (updated_at),
    INDEX       ix_wiki_note_title       (title),
    FULLTEXT INDEX ft_wiki_note_title_content (title, content) WITH PARSER ngram,

    CONSTRAINT  fk_note_category FOREIGN KEY (category_id)
        REFERENCES wiki_category(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 3. AuditLog（監査ログ）
--    FK fk_auditlog_user → auth_user は Django migrate が作成後に有効。
--    本スキーマでは FK 定義を保留。
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wiki_auditlog (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT        NULL,
    username    VARCHAR(150)  NOT NULL DEFAULT '',
    action      VARCHAR(20)   NOT NULL,
    model_name  VARCHAR(100)  NOT NULL,
    object_id   BIGINT        NOT NULL,
    summary     VARCHAR(500)  NOT NULL DEFAULT '',
    detail      JSON          NULL,
    created_at  DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX       ix_wiki_auditlog_action    (action),
    INDEX       ix_wiki_auditlog_user_id   (user_id),
    INDEX       ix_wiki_auditlog_model_obj (model_name, object_id),
    INDEX       ix_wiki_auditlog_created   (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 4. SystemConfig（動的設定）
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS wiki_systemconfig (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    `key`       VARCHAR(200) NOT NULL,
    value       LONGTEXT     NOT NULL,
    description LONGTEXT     NOT NULL,
    updated_at  DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY  uk_wiki_systemconfig_key (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ---------------------------------------------------------------------------
-- 5. Django 管理テーブル（auth / sessions / admin / contenttypes）
--    Django migrate が作成するため、ここでは定義しない。
--    migrate --fake-initial で既存テーブルとして認識させる。
-- ---------------------------------------------------------------------------
