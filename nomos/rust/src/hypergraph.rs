use std::collections::HashMap;
use uuid::Uuid;
use serde::{Deserialize, Serialize};

/// Unique identifier for a node
#[derive(Clone, Debug, Eq, PartialEq, Hash, Serialize, Deserialize)]
pub struct NodeId(Uuid);

impl NodeId {
    pub fn new() -> Self {
        NodeId(Uuid::new_v4())
    }
}

impl Default for NodeId {
    fn default() -> Self {
        Self::new()
    }
}

/// Unique identifier for an edge
#[derive(Clone, Debug, Eq, PartialEq, Hash, Serialize, Deserialize)]
pub struct EdgeId(Uuid);

impl EdgeId {
    pub fn new() -> Self {
        EdgeId(Uuid::new_v4())
    }
}

impl Default for EdgeId {
    fn default() -> Self {
        Self::new()
    }
}

/// A node in the hypergraph
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HyperNode {
    pub id: NodeId,
    pub node_type: String,
    pub content: String,
    pub metadata: HashMap<String, String>,
}

impl HyperNode {
    pub fn new(id: NodeId, node_type: String, content: String) -> Self {
        HyperNode {
            id,
            node_type,
            content,
            metadata: HashMap::new(),
        }
    }
}

/// A hyperedge connecting multiple nodes
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct HyperEdge {
    pub id: EdgeId,
    pub nodes: Vec<NodeId>,
    pub edge_type: String,
    pub weight: f64,
}

impl HyperEdge {
    pub fn new(id: EdgeId, nodes: Vec<NodeId>, edge_type: String) -> Self {
        HyperEdge {
            id,
            nodes,
            edge_type,
            weight: 1.0,
        }
    }
}

/// A hypergraph data structure
pub struct Hypergraph {
    nodes: HashMap<NodeId, HyperNode>,
    edges: HashMap<EdgeId, HyperEdge>,
    adjacency: HashMap<NodeId, Vec<NodeId>>,
}

impl Hypergraph {
    /// Create a new empty hypergraph
    pub fn new() -> Self {
        Hypergraph {
            nodes: HashMap::new(),
            edges: HashMap::new(),
            adjacency: HashMap::new(),
        }
    }

    /// Add a node to the hypergraph
    pub fn add_node(&mut self, node_type: String, content: String) -> NodeId {
        let id = NodeId::new();
        let node = HyperNode::new(id.clone(), node_type, content);
        self.nodes.insert(id.clone(), node);
        self.adjacency.insert(id.clone(), Vec::new());
        id
    }

    /// Add a hyperedge connecting multiple nodes
    pub fn add_hyperedge(&mut self, nodes: Vec<NodeId>, edge_type: String) -> EdgeId {
        let id = EdgeId::new();
        let edge = HyperEdge::new(id.clone(), nodes.clone(), edge_type);
        self.edges.insert(id.clone(), edge);

        // Update adjacency list for all connected nodes
        for node in &nodes {
            if let Some(neighbors) = self.adjacency.get_mut(node) {
                for other_node in &nodes {
                    if other_node != node && !neighbors.contains(other_node) {
                        neighbors.push(other_node.clone());
                    }
                }
            }
        }

        id
    }

    /// Retrieve a node by its ID
    pub fn get_node(&self, id: &NodeId) -> Option<&HyperNode> {
        self.nodes.get(id)
    }

    /// Retrieve an edge by its ID
    pub fn get_hyperedge(&self, id: &EdgeId) -> Option<&HyperEdge> {
        self.edges.get(id)
    }

    /// Get all neighbors of a given node
    pub fn neighbors(&self, id: &NodeId) -> Vec<NodeId> {
        self.adjacency
            .get(id)
            .map(|neighbors| neighbors.clone())
            .unwrap_or_default()
    }

    /// Get the number of nodes in the hypergraph
    pub fn num_nodes(&self) -> usize {
        self.nodes.len()
    }

    /// Get the number of edges in the hypergraph
    pub fn num_edges(&self) -> usize {
        self.edges.len()
    }
}

impl Default for Hypergraph {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_node_id_creation() {
        let id1 = NodeId::new();
        let id2 = NodeId::new();
        assert_ne!(id1, id2);
    }

    #[test]
    fn test_edge_id_creation() {
        let id1 = EdgeId::new();
        let id2 = EdgeId::new();
        assert_ne!(id1, id2);
    }
}
