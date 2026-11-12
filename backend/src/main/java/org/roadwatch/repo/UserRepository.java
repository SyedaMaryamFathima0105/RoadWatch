package org.roadwatch.repo;
import org.roadwatch.model.Models.User;import org.springframework.data.jpa.repository.JpaRepository;
public interface UserRepository extends JpaRepository<User,Long>{}
