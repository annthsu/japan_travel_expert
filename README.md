
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="src/lino.jpg" alt="Logo" width="100" height="100">
  </a>
<h3 align="center">Japan_travel_expert</h3>

</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#license">License</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


This project's main objective is to utilize GPT-4 to generate travel itineraries for Japan.

<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.



### Installation

1. Create .env file and add AZURE_OPENAI_API_KEY、AZURE_OPENAI_ENDPOINT、GOOGLE_API_KEY
2. Install packages
   ```sh
   pip install -r requirements.txt
   ```

3. Download data from google drive to data folder
   https://drive.google.com/file/d/1evMNQGVe0cCpOjL8YhnSRN6KIT8Gnh7x/view?usp=sharing

4. Run services
   ```sh
   python -m webui_pages.travel_web
   ```

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.