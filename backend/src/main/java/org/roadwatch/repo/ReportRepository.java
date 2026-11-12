package org.roadwatch.repo;
import org.roadwatch.model.Models.RoadReport;import org.roadwatch.model.Models.ReportStatus;import org.springframework.data.jpa.repository.JpaRepository;import java.util.List;
public interface ReportRepository extends JpaRepository<RoadReport,Long>{List<RoadReport> findAllByOrderByCreatedAtDesc();List<RoadReport> findByStatusOrderByCreatedAtDesc(ReportStatus status);}
