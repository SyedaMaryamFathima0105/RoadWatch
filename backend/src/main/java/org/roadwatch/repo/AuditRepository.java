package org.roadwatch.repo;
import org.roadwatch.model.Models.AuditEvent;import org.springframework.data.jpa.repository.JpaRepository;import java.util.List;
public interface AuditRepository extends JpaRepository<AuditEvent,Long>{List<AuditEvent> findByReportIdOrderByCreatedAtAsc(Long reportId);}
