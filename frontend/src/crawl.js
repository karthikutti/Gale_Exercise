import React from 'react';
import axios from 'axios';
import { Image, Button, FormGroup, ControlLabel, FormControl } from 'react-bootstrap';

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = 'X-CSRFToken';

class ShowData extends React.Component{
  render(){
    const data = this.props.images;
    const url = this.props.link;
    return (
      <div>
        <h3>{url}</h3>
        <div>
        {data.map((images,index) => (
                  <span key={index}>
                  <Image style={{width: '50px', height: '50px'}} key={index} src={images} responsive/>
                  </span>
        ))}
        </div>
      </div>
    );
  }
}

export class UserForm extends React.Component {
  constructor(props) {
    super(props);
    this.showdata = React.createRef();
    this.state = {
        depthvalue: '',
        url: '',
        data : [],
        crawlingStatus: null,
        link_url: [],
        image_urls: [],
        taskID: null,
        uniqueID: null
    };
    this.statusInterval = 1
    this.handleURLChange = this.handleURLChange.bind(this);
    this.handleDepthChange = this.handleDepthChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.checkCrawlStatus = this.checkCrawlStatus.bind(this);
    this.crawlRecursively = this.crawlRecursively.bind(this);
  }

  handleURLChange(event) {
    this.setState({url: event.target.value});
  }

  handleDepthChange(event){
    this.setState({depthvalue: event.target.value});
  }

  handleSubmit(event) {
    var self = this;
    event.preventDefault();

    if (!this.state.url){
        alert("Please enter a seed URL")
        return
    }

    var qs = require('qs');
    axios.post('crawl/api/', qs.stringify({ url: this.state.url, depth: (this.state.depthvalue ? this.state.depthvalue: 1) }))
    .then(function(resp){
        var data = resp.data;
        if (resp.data.error) {
            alert(resp.data.error)
            return
        }
        if (data.image_urls && data.link_url) {
          clearInterval(self.statusInterval)
          self.setState({
              link_url: data.link_url,
              image_urls: data.image_urls
          })
        }
        else {
            self.setState({
                taskID: resp.data.task_id,
                uniqueID: resp.data.unique_id,
                crawlingStatus: resp.status
            }, () => {
                self.statusInterval = setInterval(self.checkCrawlStatus,2000)
            });
        }
    });
}
  componentWillUnmount() {
      clearInterval(this.statusInterval)
  }

  crawlRecursively(links, depth){
    var self = this,
    params;

    params = {url: links}
    console.log('accessing db for url....' + links)
    axios.get('crawl/db/', {params})
    .then(function(resp){
        var data = resp.data;
        if (resp.data.error) {
            console.log(resp.data.error)
            return
        }
        if (data.image_urls && data.link_url) {
              self.setState(prevState => ({
                link_url : [...prevState.link_url, data.link_url]
              }))
              var new_data = {
                key: (self.state.data.length===0)?0:self.state.data[self.state.data.length-1].key+1,
                title: data.url,
                content: data.image_urls
              };
              self.setState({
                data: [...self.state.data, new_data]
              });

              data.link_url.forEach(function(link){
                if(depth > 1){
                   self.crawlRecursively(link, depth-1)
                }
              });// foreach
        }
    });//axios end
  }

  checkCrawlStatus = () => {
      var self = this,
      params = {task_id: this.state.taskID, unique_id: this.state.uniqueID };

      axios.get('crawl/api/',{params : params})
          .then(function(resp){
              var data = resp.data;
              if (data.image_urls && data.link_url) {
                  clearInterval(self.statusInterval)
                  self.setState({
                      link_url: data.link_url,
                      image_urls: data.image_urls
                  })

                  if(self.state.depthvalue > 1){
                    for(var i=0;i<data.link_url.length;i++){
                        self.crawlRecursively(data.link_url[i], self.state.depthvalue-1)
                    }
                  }
              } else if (resp.data.error) {
                  clearInterval(self.statusInterval)
                  alert(resp.data.error)
              } else if (resp.status) {
                  self.setState({
                      crawlingStatus: resp.status
                  });
              }
      });
  }

  render() {
    return (
      <div>
          <form>
            <FormGroup>
                <ControlLabel> URL: </ControlLabel>
                <FormControl type="text" autoFocus value={this.state.url} placeholder="http://www.example.com" onChange={this.handleURLChange} />
                <ControlLabel> Depth: </ControlLabel>
                <FormControl type="number" value={this.state.depthvalue} placeholder='1' min='1' max='5' onChange={this.handleDepthChange} />
                <div>
                <Button onClick={this.handleSubmit}>Submit</Button>
                </div>
            </FormGroup>
          </form>

          <div id='crawl_results'>
                <ShowData images={this.state.image_urls} link={this.state.url} />
                {this.state.data.map((data,index)=>{
                    return (
                      <ShowData key={index} images={data.content} link={data.title} />
                    )
                  })
                }
          </div>
      </div>
    );
  }
}
