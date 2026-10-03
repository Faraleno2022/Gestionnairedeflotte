# Secours MySQL : si le pilote officiel `mysqlclient` n'est pas installé mais
# que `PyMySQL` l'est, on l'enregistre comme s'il était MySQLdb. Sans effet si
# aucun des deux n'est présent (ex. base SQLite).
try:
    import pymysql  # noqa: F401

    pymysql.install_as_MySQLdb()
except Exception:
    pass
