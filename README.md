
# My Git



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/jelenailic95/git_uks">
    <img src="https://github.com/jelenailic95/git_uks/blob/master/my_git/static/my_git/images/logo.png" alt="Logo" width="100" height="80">
  </a>

  <h3 align="center">My Git</h3>

  <p align="center">
    <br />
    <a href="https://github.com/jelenailic95/git_uks"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    ·
    <a href="https://github.com/jelenailic95/git_uks/issues">Report Bug</a>
    ·
    <a href="https://github.com/jelenailic95/git_uks/issues">Request Feature</a>
  </p>
</p>




<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Project Title](#project-title)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
    * [Dependencies](#dependencies)
  * [Installation](#installation)
* [Running the tests](#running-the-tests)
* [Deployment](#deployment)
* [Versioning](#versioning)
* [Authors](#authors)


## About The Project

### Project Title

*My Git* is a student project made for the subject [Software Configuration Management](http://www.ftn.uns.ac.rs/2079040983/software-configuration-management) 2018/19.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Prerequisites

This project supports Ubuntu Linux, Windows and Mac OS.

- [Django 2.0+](https://www.djangoproject.com/)
- [PostgreSQL 10.0+](http://www.postgresql.org/)

#### Dependencies

- django  >= 2.0, < 3.0

- Pillow Pillow 5.4.1

- psycopg2 >= 2.7, < 3.0

- python-json-logger 0.1.8

- python-logstash 0.4.6

### Installation

1. Clone the repo
```
git clone https://github.com/jelenailic95/git_uks
```
2. Build 
```
docker-compose build
```
3. Run
```
docker-compose up -d
```
4. Open you browser
```
http://localhost:8000
```
5. Have fun !


## Running the tests

You can run test manually:
```
docker-compose run web python manage.py test

```
Or you can run Jenkins and check 3rd stage.
```
  def test_create_repository(self):
      repository = Repository.objects.get(name="repo")
      
      self.assertIsInstance(repository, Repository)
      self.assertEqual(repository.name, self.repository.name)
      self.assertEqual(repository.description, self.repository.description)
      self.assertEqual(repository.owner, self.user)
      self.assertEqual(repository.type, self.repository.type)
```

## Deployment




## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/jelenailic95/git_uks/tags). 

## Authors

* **David Vuletaš**     - *R1  4/2018*  - [LinkedIn](https://www.linkedin.com/in/david-vuletas-15261410b)
* **Jelena Ilić**       - *R1  6/2018*  - [LinkedIn](https://www.linkedin.com/in/david-vuletas-15261410b)
* **Marija Kovačević**  - *R1 16/2018*  - [LinkedIn](https://www.linkedin.com/in/marija-kovacevic/)

