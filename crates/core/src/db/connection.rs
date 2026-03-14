use super::config::DbConfig;
use mongodb::bson::doc;
use mongodb::{Client, Database, options::ClientOptions};

pub struct Db {
    database: Database,
}

impl Db {
    pub async fn connect(config: &DbConfig) -> Result<Self, mongodb::error::Error> {
        let options = ClientOptions::parse(&config.uri).await?;
        let client = Client::with_options(options)?;
        let database = client.database(&config.database);

        #[cfg(debug_assertions)]
        Self::ping_connection(&database).await?;

        Ok(Self { database })
    }

    pub fn handle(&self) -> &Database {
        &self.database
    }

    #[cfg(debug_assertions)]
    async fn ping_connection(db: &Database) -> Result<(), mongodb::error::Error> {
        db.run_command(doc! { "ping": 1 }).await?;
        Ok(())
    }
}
