package org.roadwatch.repo;
import org.roadwatch.model.Models.RoadIssue;import org.springframework.data.jpa.repository.JpaRepository;import java.util.List;
public interface IssueRepository extends JpaRepository<RoadIssue,Long>{List<RoadIssue> findAllByOrderByUpdatedAtDesc();}
