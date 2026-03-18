use super::config::DbConfig;
use crate::db::DbError;
use mongodb::bson::doc;
use mongodb::{Client, Collection, Database, options::ClientOptions};
use serde::{Deserialize, Serialize};

pub struct Db {
    database: Database,
}

impl Db {
    pub async fn connect(config: &DbConfig) -> Result<Self, DbError> {
        let options = ClientOptions::parse(&config.uri)
            .await
            .map_err(|e| DbError::InvalidUri(e.to_string()))?;

        let client =
            Client::with_options(options).map_err(|e| DbError::Connection(e.to_string()))?;

        let database = client.database(&config.database);

        #[cfg(debug_assertions)]
        Self::ping_connection(&database).await?;

        Ok(Self { database })
    }

    pub fn handle(&self) -> &Database {
        &self.database
    }

    /// Get a typed collection handle.  
    pub fn collection<T>(&self, name: &str) -> Collection<T>
    where
        T: Serialize + for<'de> Deserialize<'de> + Unpin + Send + Sync,
    {
        self.database.collection::<T>(name)
    }

    #[cfg(debug_assertions)]
    async fn ping_connection(db: &Database) -> Result<(), mongodb::error::Error> {
        db.run_command(doc! { "ping": 1 }).await?;
        Ok(())
    }
}
