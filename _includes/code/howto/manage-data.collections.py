# How-to: Manage-Data -> Classes
import os
import json

# ================================
# ===== INSTANTIATION-COMMON =====
# ================================

import weaviate

# Instantiate the client with the OpenAI API key
client = weaviate.connect_to_local(
    port=8080,
    grpc_port=50051,
)

# ================================
# ===== CREATE A COLLECTION =====
# ================================

# Clean slate
client.collections.delete("Article")

# START BasicCreateCollection
client.collections.create("Article")
# END BasicCreateCollection

# Test
assert client.collections.exists("Article")

# ===============================================
# ===== CREATE A COLLECTION WITH PROPERTIES =====
# ===============================================

# Clean slate
client.collections.delete("Article")

# START CreateCollectionWithProperties
import weaviate.classes as wvc

client.collections.create(
    "Article",
    properties=[
        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
        wvc.Property(name="body", data_type=wvc.DataType.TEXT),
    ]
)
# END CreateCollectionWithProperties

# Test
articles = client.collections.get("Article")
assert client.collections.exists("Article")
assert len(articles.config.get().properties) == 2

# ===============================================
# ===== CREATE A COLLECTION WITH VECTORIZER =====
# ===============================================

# Clean slate
client.collections.delete("Article")

# START Vectorizer
import weaviate.classes as wvc

client.collections.create(
    "Article",
    # highlight-start
    vectorizer_config=wvc.Configure.Vectorizer.text2vec_openai(),
    # highlight-end
    properties=[  # properties configuration is optional
        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
        wvc.Property(name="body", data_type=wvc.DataType.TEXT),
    ]
)
# END Vectorizer

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.vectorizer.value == "text2vec-openai"

# ===========================
# ===== SET VECTOR INDEX =====
# ===========================

# Clean slate
client.collections.delete("Article")

# START SetVectorIndex
import weaviate.classes as wvc

client.collections.create(
    "Article",
    vectorizer_config=wvc.Configure.Vectorizer.text2vec_openai(),
    # highlight-start
    vector_index_config=wvc.Configure.VectorIndex.hnsw(),
    # highlight-end
    properties=[
        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
        wvc.Property(name="body", data_type=wvc.DataType.TEXT),
    ]
)
# END SetVectorIndex

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.vectorizer.value == "text2vec-openai"
assert config.vector_index_type.name == "HNSW"



# ===============================================
# ===== CREATE A COLLECTION WITH A GENERATIVE MODULE =====
# ===============================================

client.collections.delete("Article")

# START SetGenerative
import weaviate.classes as wvc

client.collections.create(
    "Article",
    vectorizer_config=wvc.Configure.Vectorizer.text2vec_openai(),
    # highlight-start
    generative_config=wvc.Configure.Generative.openai(),
    # highlight-end
    properties=[ # properties configuration is optional
        wvc.Property(name="title", data_type=wvc.DataType.TEXT),
        wvc.Property(name="body", data_type=wvc.DataType.TEXT),
    ]
)
# END SetGenerative

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.generative_config.generator == "generative-openai"

# Delete the collection to recreate it
client.collections.delete("Article")


# ===========================
# ===== MODULE SETTINGS =====
# ===========================

# Clean slate
client.collections.delete("Article")

# START ModuleSettings
import weaviate.classes as wvc

client.collections.create(
    "Article",
    # highlight-start
    vectorizer_config=wvc.Configure.Vectorizer.text2vec_cohere(
        model="embed-multilingual-v2.0",
        vectorize_collection_name=True
    ),
    # highlight-end
)
# END ModuleSettings

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.vectorizer.value == "text2vec-cohere"
assert config.vectorizer_config.model["model"] == "embed-multilingual-v2.0"

# ====================================
# ===== MODULE SETTINGS PROPERTY =====
# ====================================

# Clean slate
client.collections.delete("Article")

# START PropModuleSettings
import weaviate.classes as wvc

client.collections.create(
    "Article",
    vectorizer_config=wvc.Configure.Vectorizer.text2vec_huggingface(),

    properties=[
        wvc.Property(
            name="title",
            data_type=wvc.DataType.TEXT,
            # highlight-start
            vectorize_property_name=True,  # Use "title" as part of the value to vectorize
            tokenization=wvc.Tokenization.LOWERCASE  # Use "lowecase" tokenization
            # highlight-end
        ),
        wvc.Property(
            name="body",
            data_type=wvc.DataType.TEXT,
            # highlight-start
            skip_vectorization=True,  # Don't vectorize this property
            tokenization=wvc.Tokenization.WHITESPACE  # Use "whitespace" tokenization
            # highlight-end
        ),
    ]
)
# END PropModuleSettings

# Test
collection = client.collections.get("Article")
config = collection.config.get()

assert config.vectorizer.value == "text2vec-huggingface"
for p in config.properties:
    if p.name == "title":
        assert p.tokenization.name == "LOWERCASE"
    elif p.name == "body":
        assert p.tokenization.name == "WHITESPACE"


# ===========================
# ===== DISTANCE METRIC =====
# ===========================

# Clean slate
client.collections.delete("Article")

# START DistanceMetric
import weaviate.classes as wvc

client.collections.create(
    "Article",
    # highlight-start
    vector_index_config=wvc.Configure.VectorIndex.hnsw(
        distance_metric=wvc.VectorDistance.COSINE
    ),
    # highlight-end
)
# END DistanceMetric

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.vector_index_config.distance_metric.value == "cosine"

# =======================
# ===== REPLICATION =====
# =======================

# Clean slate
client.collections.delete("Article")

# Connect to a setting with 3 replicas
client = weaviate.connect_to_local(
    port=8180
)

# START ReplicationSettings
import weaviate.classes as wvc

client.collections.create(
    "Article",
    # highlight-start
    replication_config=wvc.Configure.replication(
        factor=3
    )
    # highlight-end
)
# END ReplicationSettings

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.replication_config.factor == 3

# ====================
# ===== SHARDING =====
# ====================

client = weaviate.connect_to_local()

# Clean slate
client.collections.delete("Article")

# START ShardingSettings
import weaviate.classes as wvc

client.collections.create(
    "Article",
    # highlight-start
    sharding_config=wvc.Configure.sharding(
        virtual_per_physical=128,
        desired_count=1,
        actual_count=1,
        desired_virtual_count=128,
        actual_virtual_count=128,
    )
    # highlight-end
)
# END ShardingSettings

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.sharding_config.virtual_per_physical == 128
assert config.sharding_config.desired_count == 1
assert config.sharding_config.actual_count == 1
assert config.sharding_config.desired_virtual_count == 128
assert config.sharding_config.actual_virtual_count == 128

# =========================
# ===== MULTI-TENANCY =====
# =========================

# Clean slate
client.collections.delete("Article")

# START Multi-tenancy
client.collections.create(
    "Article",
    # highlight-start
    multi_tenancy_config=wvc.Configure.multi_tenancy(True)
    # highlight-end
)
# END Multi-tenancy

collection = client.collections.get("Article")
config = collection.config.get()
assert config.multi_tenancy_config.enabled == True

# ==========================
# ===== ADD A PROPERTY =====
# ==========================

# START AddProp
import weaviate.classes as wvc

# Get the Article collection object
articles = client.collections.get("Article")

# Add a new property
articles.config.add_property(
    # highlight-start
    prop=wvc.Property(
        name="body",
        data_type=wvc.DataType.TEXT
    )
    # highlight-end
)
# END AddProp

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert len(config.properties) == 1
assert config.properties[0].name == "body"

# ==============================
# ===== MODIFY A PARAMETER =====
# ==============================

# START ModifyParam
import weaviate.classes as wvc

# Get the Article collection object
articles = client.collections.get("Article")

# Update the collection configuration
# highlight-start
articles.config.update(
    # Note, use Reconfigure here (not Configure)
    inverted_index_config=wvc.Reconfigure.inverted_index(
        stopwords_removals=["a", "the"]
    )
)
# highlight-end
# END ModifyParam

# Test
collection = client.collections.get("Article")
config = collection.config.get()
assert config.inverted_index_config.stopwords.removals == ["a", "the"]

# ================================
# ===== READ A COLLECTION =====
# ================================

# START ReadOneCollection
articles = client.collections.get("Article")
articles_config = articles.config.get()

print(articles_config)
# END ReadOneCollection

assert articles_config.name == "Article"


# ================================
# ===== READ ALL COLLECTIONS =====
# ================================

# START ReadAllCollections
response = client.collections.list_all()

print(response)
# END ReadAllCollections

assert type(response) == dict
assert "Article" in response


# ================================
# ===== UPDATE A COLLECTION =====
# ================================

# Clean slate
client.collections.delete("Article")

# Define and create a collection
client.collections.create(
    name="Article",
    inverted_index_config=wvc.Configure.inverted_index(
        bm25_b=0.7,
        bm25_k1=1.2
    )
)
old_config = articles.config.get()


# Create an object to check that it remains mutable
for _ in range(5):
    articles.data.insert({
        "title": "A grand day out."
    })


# START UpdateCollection
import weaviate.classes as wvc

articles = client.collections.get("Article")

# Update the collection definition
articles.config.update(
    inverted_index_config=wvc.Reconfigure.inverted_index(
        bm25_k1=1.5
    )
)
# END UpdateCollection

new_config = articles.config.get()

assert old_config.inverted_index_config.bm25.k1 == 1.2
assert new_config.inverted_index_config.bm25.k1 == 1.5