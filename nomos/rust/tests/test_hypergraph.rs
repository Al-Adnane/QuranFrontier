use frontier_core_rust::hypergraph::Hypergraph;

#[test]
fn test_hypergraph_node_creation() {
    let mut graph = Hypergraph::new();

    // Add nodes
    let node1 = graph.add_node("compute".to_string(), "A1".to_string());
    let node2 = graph.add_node("memory".to_string(), "B1".to_string());

    // Retrieve nodes
    let retrieved_node1 = graph.get_node(&node1);
    assert!(retrieved_node1.is_some());

    let retrieved_node2 = graph.get_node(&node2);
    assert!(retrieved_node2.is_some());

    // Verify node properties
    assert_eq!(retrieved_node1.unwrap().node_type, "compute");
    assert_eq!(retrieved_node1.unwrap().content, "A1");
    assert_eq!(retrieved_node2.unwrap().node_type, "memory");
    assert_eq!(retrieved_node2.unwrap().content, "B1");

    // Verify total nodes
    assert_eq!(graph.num_nodes(), 2);
}

#[test]
fn test_hypergraph_hyperedge_creation() {
    let mut graph = Hypergraph::new();

    // Create nodes
    let node1 = graph.add_node("compute".to_string(), "A1".to_string());
    let node2 = graph.add_node("memory".to_string(), "B1".to_string());
    let node3 = graph.add_node("storage".to_string(), "C1".to_string());

    // Create hyperedge between nodes
    let edge1 = graph.add_hyperedge(
        vec![node1.clone(), node2.clone()],
        "connects".to_string(),
    );

    let edge2 = graph.add_hyperedge(
        vec![node2.clone(), node3.clone()],
        "transfers".to_string(),
    );

    // Retrieve edges
    let retrieved_edge1 = graph.get_hyperedge(&edge1);
    assert!(retrieved_edge1.is_some());

    let retrieved_edge2 = graph.get_hyperedge(&edge2);
    assert!(retrieved_edge2.is_some());

    // Verify edge properties
    assert_eq!(retrieved_edge1.unwrap().edge_type, "connects");
    assert_eq!(retrieved_edge1.unwrap().nodes.len(), 2);
    assert_eq!(retrieved_edge2.unwrap().edge_type, "transfers");

    // Verify total edges
    assert_eq!(graph.num_edges(), 2);
}

#[test]
fn test_hypergraph_traversal() {
    let mut graph = Hypergraph::new();

    // Create a small graph
    let node1 = graph.add_node("compute".to_string(), "A1".to_string());
    let node2 = graph.add_node("memory".to_string(), "B1".to_string());
    let node3 = graph.add_node("storage".to_string(), "C1".to_string());

    // Connect nodes
    graph.add_hyperedge(
        vec![node1.clone(), node2.clone()],
        "connects".to_string(),
    );

    graph.add_hyperedge(
        vec![node1.clone(), node3.clone()],
        "connects".to_string(),
    );

    // Test neighbors of node1
    let neighbors = graph.neighbors(&node1);
    assert_eq!(neighbors.len(), 2);
    assert!(neighbors.iter().any(|n| n == &node2));
    assert!(neighbors.iter().any(|n| n == &node3));

    // Test neighbors of node2
    let neighbors2 = graph.neighbors(&node2);
    assert_eq!(neighbors2.len(), 1);
    assert!(neighbors2.iter().any(|n| n == &node1));

    // Test neighbors of node3
    let neighbors3 = graph.neighbors(&node3);
    assert_eq!(neighbors3.len(), 1);
    assert!(neighbors3.iter().any(|n| n == &node1));
}
