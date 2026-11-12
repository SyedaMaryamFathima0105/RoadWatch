package org.roadwatch.api;
import org.springframework.context.annotation.*;import org.springframework.web.servlet.config.annotation.*;import org.springframework.beans.factory.annotation.Value;import org.springframework.web.filter.OncePerRequestFilter;import jakarta.servlet.*;import jakarta.servlet.http.*;import java.io.IOException;
@Configuration public class WebConfig implements WebMvcConfigurer {
 @Value("${roadwatch.upload-dir}")String uploadDir;
 @Override public void addResourceHandlers(ResourceHandlerRegistry r){r.addResourceHandler("/uploads/**").addResourceLocations("file:"+java.nio.file.Path.of(uploadDir).toAbsolutePath()+"/");}
 @Override public void addCorsMappings(CorsRegistry r){r.addMapping("/api/**").allowedOrigins("http://localhost:5173").allowedMethods("GET","POST","PATCH","OPTIONS").allowedHeaders("Content-Type","X-Admin-Key");}
 @Bean org.springframework.boot.web.servlet.FilterRegistrationBean<OncePerRequestFilter> requestLogging(){OncePerRequestFilter filter=new OncePerRequestFilter(){@Override protected void doFilterInternal(HttpServletRequest req,HttpServletResponse res,FilterChain chain)throws ServletException,IOException{long start=System.nanoTime();try{chain.doFilter(req,res);}finally{System.out.printf("%s %s -> %d (%d ms)%n",req.getMethod(),req.getRequestURI(),res.getStatus(),(System.nanoTime()-start)/1_000_000);}}};org.springframework.boot.web.servlet.FilterRegistrationBean<OncePerRequestFilter> bean=new org.springframework.boot.web.servlet.FilterRegistrationBean<>(filter);bean.setOrder(1);return bean;}
 @Bean org.springframework.security.web.SecurityFilterChain security(org.springframework.security.config.annotation.web.builders.HttpSecurity http,@Value("${roadwatch.admin-api-key}")String key)throws Exception{
  OncePerRequestFilter adminKeyFilter=new OncePerRequestFilter(){@Override protected void doFilterInternal(HttpServletRequest req,HttpServletResponse res,FilterChain chain)throws ServletException,IOException{
   if(req.getRequestURI().startsWith("/api/admin/")&&java.security.MessageDigest.isEqual(req.getHeader("X-Admin-Key")==null?new byte[0]:req.getHeader("X-Admin-Key").getBytes(),key.getBytes()))org.springframework.security.core.context.SecurityContextHolder.getContext().setAuthentication(new org.springframework.security.authentication.UsernamePasswordAuthenticationToken("prototype-admin",null,java.util.List.of(new org.springframework.security.core.authority.SimpleGrantedAuthority("ROLE_ADMIN"))));
   chain.doFilter(req,res);
  }};
  return http.csrf(c->c.disable()).cors(org.springframework.security.config.Customizer.withDefaults()).addFilterBefore(adminKeyFilter,org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter.class).authorizeHttpRequests(a->a.requestMatchers("/api/admin/**").hasRole("ADMIN").anyRequest().permitAll()).build();
 }
}
