package org.roadwatch.model;
import jakarta.persistence.*;import java.time.Instant;
public final class Models { private Models(){}
 public enum Role{CITIZEN,ADMIN} public enum ReportStatus{SUBMITTED,AI_FLAGGED,UNDER_REVIEW,ACCEPTED,REJECTED,REPAIRED} public enum IssueStatus{OPEN,UNDER_REVIEW,ACCEPTED,REPAIRED}
 @Entity @Table(name="citizens") public static class User { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) public Long id; public String name; @Column(unique=true) public String email; @Enumerated(EnumType.STRING) public Role role=Role.CITIZEN; public Instant createdAt=Instant.now(); }
 @Entity public static class RoadIssue { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) public Long id; public String title; public String damageType; public double latitude,longitude; @Enumerated(EnumType.STRING) public IssueStatus status=IssueStatus.OPEN; public int reportCount=1; public Instant createdAt=Instant.now(),updatedAt=Instant.now(); }
 @Entity public static class RoadReport { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) public Long id; public Long userId; public String imageUrl; public Double latitude,longitude; @Column(length=2000) public String note; @Enumerated(EnumType.STRING) public ReportStatus status=ReportStatus.SUBMITTED; public Double aiConfidence; public String detectedDamageType; public Long issueId; public Instant createdAt=Instant.now(),updatedAt=Instant.now(); }
 @Entity public static class AuditEvent { @Id @GeneratedValue(strategy=GenerationType.IDENTITY) public Long id; public Long reportId,actorId; public String action; @Column(length=2000) public String details; public Instant createdAt=Instant.now(); }
}
